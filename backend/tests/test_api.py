import unittest
from app.main import app

class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
    def test_health(self):
        self.assertEqual(self.client.get('/api/health').status_code, 200)
    def test_summary_has_counts(self):
        body = self.client.get('/api/summary').get_json()
        self.assertIn('total_alerts', body)
        self.assertIn('severity_counts', body)
    def test_alert_list(self):
        response = self.client.get('/api/alerts')
        self.assertEqual(response.status_code, 200)
        self.assertGreater(response.get_json()['count'], 0)
    def test_invalid_status(self):
        response = self.client.patch('/api/alerts/SOC-2026-1042/status', json={'status':'hacked'})
        self.assertEqual(response.status_code, 400)
    def test_event_ingestion(self):
        response = self.client.post('/api/events', json={'title':'Test event','severity':'Low','source':'pytest'})
        self.assertEqual(response.status_code, 201)

if __name__ == '__main__': unittest.main()
