import unittest

from app.core.logging import redact_sensitive_data
from app.core.rate_limiter import limiter


class TestPhase8Hardening(unittest.TestCase):
    def setUp(self):
        limiter._redis_client = None
        limiter._in_memory.history.clear()

    def test_rate_limiter_rejects_excess_requests(self):
        test_ip = "192.0.2.42"
        for _ in range(10):
            allowed, _, _, _ = limiter.is_allowed(test_ip, "/api/v1/submissions/")
            self.assertTrue(allowed)
        allowed, _, _, retry_after = limiter.is_allowed(test_ip, "/api/v1/submissions/")
        self.assertFalse(allowed)
        self.assertGreater(retry_after, 0)

    def test_secret_redaction_in_logs(self):
        sample_token = "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0In0.sig"
        redacted_token = redact_sensitive_data(sample_token)
        self.assertNotIn("eyJhbGciOiJIUzI1NiJ9", redacted_token)
        self.assertIn("Bearer [REDACTED_TOKEN]", redacted_token)

        sample_dsn = "postgresql://cipheruser:secret_pg_pass@db:5432/cipherpagedb"
        redacted_dsn = redact_sensitive_data(sample_dsn)
        self.assertNotIn("secret_pg_pass", redacted_dsn)
        self.assertIn(":[REDACTED_PASS]@", redacted_dsn)

        sample_pwd = '{"username": "student", "password": "SuperSecretPassword123"}'
        redacted_pwd = redact_sensitive_data(sample_pwd)
        self.assertNotIn("SuperSecretPassword123", redacted_pwd)
        self.assertIn('"password": "[REDACTED_PASSWORD]"', redacted_pwd)

    @unittest.skip("Requires a dedicated seeded API, Firebase token, Neon test database, Redis, and worker.")
    def test_live_learning_cycle(self):
        self.fail("Run live-service tests only through a separately provisioned isolated test harness.")


if __name__ == "__main__":
    unittest.main()
