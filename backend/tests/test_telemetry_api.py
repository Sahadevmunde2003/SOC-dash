import unittest

from app.main import app


class TelemetryEndpointTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_auth_ingestion_requires_content_string(self):
        response = self.client.post("/api/ingest/auth-log", json={})
        self.assertEqual(response.status_code, 400)

    def test_auth_ingestion_returns_parse_counts(self):
        raw = "\n".join([
            "Oct 18 12:59:01 ubuntu-dmz sshd[1]: Failed password for labuser from 192.0.2.24 port 51231 ssh2",
            "Oct 18 12:59:15 ubuntu-dmz sshd[2]: Failed password for labuser from 192.0.2.24 port 51232 ssh2",
            "Oct 18 12:59:28 ubuntu-dmz sshd[3]: Failed password for labuser from 192.0.2.24 port 51233 ssh2",
            "Oct 18 12:59:42 ubuntu-dmz sshd[4]: Failed password for labuser from 192.0.2.24 port 51234 ssh2",
            "Oct 18 12:59:59 ubuntu-dmz sshd[5]: Failed password for labuser from 192.0.2.24 port 51235 ssh2",
        ])
        response = self.client.post("/api/ingest/auth-log", json={"content": raw})
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["parsed_count"], 5)
        self.assertEqual(body["detections"][0]["rule_id"], "SSH-BRUTE-001")

    def test_pfsense_ingestion_parses_jsonl(self):
        raw = '{"timestamp":"2026-10-18T12:18:00Z","action":"block","protocol":"tcp","src_ip":"198.51.100.77","dst_ip":"10.10.20.10","dst_port":22}'
        response = self.client.post("/api/ingest/pfsense", json={"content": raw})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["parsed_count"], 1)


if __name__ == "__main__":
    unittest.main()
