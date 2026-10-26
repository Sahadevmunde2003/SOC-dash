"""Sentinel SOC REST API. Demo-only in-memory store; secure and persist before deployment."""
from datetime import datetime, timezone
import uuid

from flask import Flask, jsonify, request
from flask_cors import CORS

from app.data import ALERTS, get_alerts, summary
from app.telemetry import detect_events, parse_auth_log, parse_pfsense_jsonl

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}})
VALID_STATUSES = {"New", "Investigating", "Contained", "Closed", "False Positive"}
VALID_SEVERITIES = {"Critical", "High", "Medium", "Low"}


def _store_detections(detections):
    """Add detections to the demo alert list and return the stored records."""
    stored = []
    for detection in detections:
        item = dict(detection)
        item["id"] = "SOC-" + uuid.uuid4().hex[:8].upper()
        item["status"] = "New"
        item["timestamp"] = item.get("timestamp") or datetime.now(timezone.utc).isoformat()
        ALERTS.insert(0, item)
        stored.append(item)
    return stored


def _ingest_raw(parser):
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or not isinstance(payload.get("content"), str):
        return jsonify({"error": "expected_json_content_string"}), 400
    events, errors = parser(payload["content"])
    detections = _store_detections(detect_events(events))
    return jsonify({
        "parsed_count": len(events),
        "error_count": len(errors),
        "errors": errors,
        "events": events,
        "detections": detections,
        "note": "Parsed events are returned in this response; generated alerts are held in memory and reset when the API restarts.",
    }), 200


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "sentinel-soc-api", "mode": "demo"})


@app.get("/api/summary")
def dashboard_summary():
    return jsonify(summary())


@app.get("/api/alerts")
def alerts():
    items = get_alerts(
        request.args.get("q", ""),
        request.args.get("severity", "All"),
        request.args.get("status", "All"),
    )
    return jsonify({"items": items, "count": len(items)})


@app.get("/api/alerts/<alert_id>")
def alert_detail(alert_id):
    item = next((a for a in ALERTS if a["id"] == alert_id), None)
    if not item:
        return jsonify({"error": "alert_not_found"}), 404
    return jsonify(item)


@app.patch("/api/alerts/<alert_id>/status")
def update_status(alert_id):
    payload = request.get_json(silent=True) or {}
    status = payload.get("status")
    if status not in VALID_STATUSES:
        return jsonify({"error": "invalid_status", "allowed": sorted(VALID_STATUSES)}), 400
    item = next((a for a in ALERTS if a["id"] == alert_id), None)
    if not item:
        return jsonify({"error": "alert_not_found"}), 404
    item["status"] = status
    if payload.get("note"):
        item.setdefault("analyst_notes", []).append(str(payload["note"])[:1000])
    return jsonify(item)


@app.post("/api/events")
def ingest_event():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "expected_json_object"}), 400
    required = ["title", "severity", "source"]
    missing = [key for key in required if not payload.get(key)]
    if missing:
        return jsonify({"error": "missing_fields", "fields": missing}), 400
    if payload["severity"] not in VALID_SEVERITIES:
        return jsonify({"error": "invalid_severity"}), 400
    item = {
        "id": "SOC-" + uuid.uuid4().hex[:8].upper(),
        "title": str(payload["title"])[:200],
        "severity": payload["severity"],
        "status": "New",
        "source": str(payload["source"])[:100],
        "src_ip": str(payload.get("src_ip", "unknown"))[:64],
        "dst_ip": str(payload.get("dst_ip", "unknown"))[:64],
        "timestamp": str(payload.get("timestamp", "")) or datetime.now(timezone.utc).isoformat(),
        "technique": str(payload.get("technique", "Unmapped"))[:30],
        "technique_name": str(payload.get("technique_name", "Unmapped"))[:100],
        "description": str(payload.get("description", "Ingested lab event"))[:1000],
        "evidence": payload.get("evidence", []) if isinstance(payload.get("evidence", []), list) else [],
    }
    ALERTS.insert(0, item)
    return jsonify(item), 201


@app.post("/api/ingest/auth-log")
def ingest_auth_log():
    return _ingest_raw(parse_auth_log)


@app.post("/api/ingest/pfsense")
def ingest_pfsense():
    return _ingest_raw(parse_pfsense_jsonl)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
