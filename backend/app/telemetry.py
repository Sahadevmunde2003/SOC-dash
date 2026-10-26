"""Parsers and lightweight detections for authorized SOC lab telemetry."""
from collections import defaultdict
from datetime import datetime, timedelta, timezone
import ipaddress
import json
import re

AUTH_RE = re.compile(
    r"^(?P<month>[A-Z][a-z]{2})\s+(?P<day>\d{1,2})\s+"
    r"(?P<clock>\d{2}:\d{2}:\d{2})\s+(?P<host>\S+)\s+sshd\[\d+\]:\s+"
    r"(?P<message>.+)$"
)
FAILED_RE = re.compile(
    r"Failed password for (?:invalid user )?(?P<user>\S+) from "
    r"(?P<ip>\S+) port (?P<port>\d+)"
)
ACCEPTED_RE = re.compile(
    r"Accepted (?:password|publickey) for (?P<user>\S+) from "
    r"(?P<ip>\S+) port (?P<port>\d+)"
)


def _valid_ip(value):
    try:
        return str(ipaddress.ip_address(str(value)))
    except (ValueError, TypeError):
        raise ValueError("invalid_ip")


def _iso_timestamp(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("invalid_timestamp")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        raise ValueError("invalid_timestamp")
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_auth_log(content, year=None):
    """Parse sshd authentication records; return (events, errors)."""
    year = year or datetime.now(timezone.utc).year
    events, errors = [], []
    for line_number, line in enumerate(str(content).splitlines(), 1):
        if not line.strip():
            continue
        match = AUTH_RE.match(line.strip())
        if not match:
            errors.append({"line": line_number, "error": "unrecognized_auth_line"})
            continue
        message = match.group("message")
        kind_match = FAILED_RE.search(message)
        event_type = "failed_login"
        if not kind_match:
            kind_match = ACCEPTED_RE.search(message)
            event_type = "successful_login"
        if not kind_match:
            continue
        try:
            source_ip = _valid_ip(kind_match.group("ip"))
            stamp = datetime.strptime(
                f"{year} {match.group('month')} {match.group('day')} {match.group('clock')}",
                "%Y %b %d %H:%M:%S",
            ).replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
        except (ValueError, OverflowError):
            errors.append({"line": line_number, "error": "invalid_auth_record"})
            continue
        events.append({
            "timestamp": stamp,
            "source": "Ubuntu auth",
            "sensor": match.group("host"),
            "event_type": event_type,
            "src_ip": source_ip,
            "dst_ip": "unknown",
            "username": kind_match.group("user"),
            "source_port": int(kind_match.group("port")),
            "raw": line.strip(),
        })
    return events, errors


def parse_pfsense_jsonl(content):
    """Parse newline-delimited JSON firewall records; return (events, errors)."""
    events, errors = [], []
    for line_number, line in enumerate(str(content).splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError("expected_object")
            timestamp = _iso_timestamp(row.get("timestamp"))
            src_ip = _valid_ip(row.get("src_ip"))
            dst_ip = _valid_ip(row.get("dst_ip"))
            action = str(row.get("action", "")).lower()
            if action not in {"pass", "block", "reject"}:
                raise ValueError("invalid_action")
            protocol = str(row.get("protocol", "unknown")).lower()
            events.append({
                "timestamp": timestamp,
                "source": "pfSense firewall",
                "sensor": str(row.get("sensor", "pfsense-lab"))[:100],
                "event_type": "firewall_" + action,
                "action": action,
                "protocol": protocol[:20],
                "src_ip": src_ip,
                "dst_ip": dst_ip,
                "src_port": row.get("src_port"),
                "dst_port": row.get("dst_port"),
                "raw": row,
            })
        except (json.JSONDecodeError, ValueError, TypeError) as exc:
            errors.append({"line": line_number, "error": str(exc) or "invalid_record"})
    return events, errors


def detect_events(events, ssh_threshold=5, ssh_window_seconds=120, block_threshold=5):
    """Create alert payloads from normalized events; thresholds are demo defaults."""
    alerts = []
    failed = defaultdict(list)
    blocked = defaultdict(list)
    for event in events:
        if event.get("event_type") == "failed_login":
            failed[event["src_ip"]].append(event)
        if event.get("event_type") in {"firewall_block", "firewall_reject"}:
            blocked[event["src_ip"]].append(event)

    for source_ip, attempts in failed.items():
        attempts.sort(key=lambda item: item["timestamp"])
        for start_index, start in enumerate(attempts):
            start_time = datetime.fromisoformat(start["timestamp"].replace("Z", "+00:00"))
            window = [
                item for item in attempts[start_index:]
                if datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00"))
                <= start_time + timedelta(seconds=ssh_window_seconds)
            ]
            if len(window) >= ssh_threshold:
                alerts.append({
                    "title": "Repeated SSH authentication failures",
                    "severity": "High",
                    "source": "Ubuntu auth",
                    "src_ip": source_ip,
                    "dst_ip": "unknown",
                    "timestamp": window[-1]["timestamp"],
                    "technique": "T1110",
                    "technique_name": "Brute Force",
                    "description": f"{len(window)} failed SSH logins from {source_ip} within {ssh_window_seconds} seconds.",
                    "evidence": [f"Failed attempts in window: {len(window)}", "Rule: SSH-BRUTE-001"],
                    "rule_id": "SSH-BRUTE-001",
                })
                break

    for source_ip, attempts in blocked.items():
        if len(attempts) >= block_threshold:
            ports = sorted({str(item.get("dst_port")) for item in attempts if item.get("dst_port") is not None})
            alerts.append({
                "title": "Repeated blocked inbound connections",
                "severity": "Low",
                "source": "pfSense firewall",
                "src_ip": source_ip,
                "dst_ip": attempts[-1]["dst_ip"],
                "timestamp": max(item["timestamp"] for item in attempts),
                "technique": "T1046",
                "technique_name": "Network Service Discovery",
                "description": f"{len(attempts)} blocked/rejected connections from {source_ip}; review whether this resembles probing.",
                "evidence": [f"Blocked events: {len(attempts)}", "Destination ports: " + (", ".join(ports) or "not provided"), "Rule: PFSENSE-DENY-BURST-001"],
                "rule_id": "PFSENSE-DENY-BURST-001",
            })
    return alerts
