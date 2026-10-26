import unittest

from app.telemetry import detect_events, parse_auth_log, parse_pfsense_jsonl


class TelemetryParserTests(unittest.TestCase):
    def test_auth_log_parses_failed_and_successful_login(self):
        raw = "\n".join([
            "Oct 18 12:59:03 ubuntu-dmz sshd[2241]: Failed password for labuser from 192.0.2.24 port 51231 ssh2",
            "Oct 18 13:01:11 ubuntu-dmz sshd[2245]: Accepted publickey for labuser from 10.10.20.5 port 49220 ssh2",
        ])
        events, errors = parse_auth_log(raw, year=2026)
        self.assertEqual(errors, [])
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["event_type"], "failed_login")
        self.assertEqual(events[1]["event_type"], "successful_login")

    def test_auth_log_detects_five_failures_in_window(self):
        lines = [
            f"Oct 18 12:59:{second:02d} ubuntu-dmz sshd[{1000 + second}]: Failed password for labuser from 192.0.2.24 port {50000 + second} ssh2"
            for second in [1, 15, 28, 42, 59]
        ]
        events, errors = parse_auth_log("\n".join(lines), year=2026)
        detections = detect_events(events)
        self.assertEqual(errors, [])
        self.assertEqual(len(detections), 1)
        self.assertEqual(detections[0]["rule_id"], "SSH-BRUTE-001")
        self.assertEqual(detections[0]["severity"], "High")

    def test_pfsense_jsonl_validates_and_parses(self):
        raw = '{"timestamp":"2026-10-18T12:18:00Z","sensor":"pfsense-lab","action":"pass","protocol":"tcp","src_ip":"10.10.20.15","dst_ip":"203.0.113.42","dst_port":443}\nnot-json'
        events, errors = parse_pfsense_jsonl(raw)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_type"], "firewall_pass")
        self.assertEqual(len(errors), 1)

    def test_pfsense_repeated_blocks_generate_detection(self):
        events = []
        for port in [22, 80, 443, 8080, 8443]:
            events.append({
                "timestamp": "2026-10-18T12:18:00Z",
                "event_type": "firewall_block",
                "src_ip": "198.51.100.77",
                "dst_ip": "10.10.20.10",
                "dst_port": port,
            })
        detections = detect_events(events)
        self.assertEqual(len(detections), 1)
        self.assertEqual(detections[0]["rule_id"], "PFSENSE-DENY-BURST-001")


if __name__ == "__main__":
    unittest.main()
