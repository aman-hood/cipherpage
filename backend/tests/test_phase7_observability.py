import unittest
import json
import urllib.request
from app.core.metrics import normalize_endpoint, DATABASE_HEALTH_STATUS, REDIS_HEALTH_STATUS

class TestPhase7Observability(unittest.TestCase):
    def test_01_path_normalization(self):
        """Verify dynamic IDs are normalized to prevent label cardinality explosion."""
        self.assertEqual(
            normalize_endpoint("/api/v1/challenges/486"),
            "/api/v1/challenges/{id}"
        )
        self.assertEqual(
            normalize_endpoint("/api/v1/courses/10/lectures/2"),
            "/api/v1/courses/{id}/lectures/{id}"
        )
        self.assertEqual(
            normalize_endpoint("/api/v1/users/550e8400-e29b-41d4-a716-446655440000"),
            "/api/v1/users/{uuid}"
        )

    def test_02_health_endpoint_returns_subsystems(self):
        """Verify /health returns structured subsystems and HTTP 200 (NFR-04, NFR-06)."""
        with urllib.request.urlopen("http://localhost:8000/health") as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode())
            self.assertEqual(data.get("status"), "ok")
            self.assertIn("subsystems", data)
            self.assertEqual(data["subsystems"].get("database"), "healthy")

    def test_03_metrics_endpoint_exposition(self):
        """Verify /metrics returns standard Prometheus text format with platform metrics (OPS-09, AC-09)."""
        with urllib.request.urlopen("http://localhost:8000/metrics") as response:
            self.assertEqual(response.status, 200)
            content = response.read().decode()
            
            # Verify core metrics are present in Prometheus text exposition
            self.assertIn("cipherpage_http_requests_total", content)
            self.assertIn("cipherpage_http_request_duration_seconds", content)
            self.assertIn("cipherpage_database_health_status", content)
            self.assertIn("cipherpage_redis_health_status", content)
            
            # Verify AC-09: No secrets or raw database passwords leaked
            self.assertNotIn("cipherpassword", content)
            self.assertNotIn("supersecretjwtkey", content)

    def test_04_health_gauges_active(self):
        """Verify Prometheus health gauges reflect operational readiness."""
        self.assertEqual(DATABASE_HEALTH_STATUS._value.get(), 1.0)
        self.assertEqual(REDIS_HEALTH_STATUS._value.get(), 1.0)

if __name__ == "__main__":
    unittest.main()
