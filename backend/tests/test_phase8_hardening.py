import unittest
import json
import urllib.request
import urllib.error
from app.core.logging import redact_sensitive_data
from app.core.rate_limiter import limiter
from app.database.session import SessionLocal
from app.models.ai import AIUsageRecord

class TestPhase8Hardening(unittest.TestCase):
    def setUp(self):
        limiter.history.clear()
        try:
            db = SessionLocal()
            db.query(AIUsageRecord).delete()
            db.commit()
            db.close()
        except Exception:
            pass
    def test_01_security_headers_present(self):
        """Verify OWASP recommended security response headers on all endpoints (SEC-02)."""
        req = urllib.request.Request("http://localhost:8000/health")
        with urllib.request.urlopen(req) as resp:
            headers = dict(resp.headers)
            self.assertEqual(headers.get("x-content-type-options"), "nosniff")
            self.assertEqual(headers.get("x-frame-options"), "DENY")
            self.assertEqual(headers.get("x-xss-protection"), "1; mode=block")
            self.assertIn("max-age=31536000", headers.get("strict-transport-security", ""))
            self.assertIn("default-src 'self'", headers.get("content-security-policy", ""))
            self.assertEqual(headers.get("referrer-policy"), "strict-origin-when-cross-origin")
            self.assertIn("geolocation=()", headers.get("permissions-policy", ""))

    def test_02_rate_limiter_headers_and_throttling(self):
        """Verify sliding-window rate limiter returns headers and limits burst traffic (SEC-02, CODE-03)."""
        req = urllib.request.Request("http://localhost:8000/api/v1/challenges/")
        with urllib.request.urlopen(req) as resp:
            self.assertIn("x-ratelimit-limit", dict(resp.headers))
            self.assertIn("x-ratelimit-remaining", dict(resp.headers))

        # Test limiter logic directly with custom identifier
        test_ip = "192.0.2.42"
        # Consume the submissions quota (10 per minute)
        for _ in range(10):
            allowed, remaining, limit, _ = limiter.is_allowed(test_ip, "/api/v1/submissions/")
            self.assertTrue(allowed)

        # 11th request must be rejected
        allowed, remaining, limit, retry_after = limiter.is_allowed(test_ip, "/api/v1/submissions/")
        self.assertFalse(allowed)
        self.assertGreater(retry_after, 0)

    def test_03_secret_redaction_in_logs(self):
        """Verify sensitive tokens, passwords, and connection strings are redacted (SEC-04)."""
        sample_token = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0In0"
        redacted = redact_sensitive_data(sample_token)
        self.assertNotIn("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", redacted)
        self.assertIn("Bearer [REDACTED_TOKEN]", redacted)

        sample_dsn = "postgresql://cipheruser:secret_pg_pass@db:5432/cipherpagedb"
        redacted_dsn = redact_sensitive_data(sample_dsn)
        self.assertNotIn("secret_pg_pass", redacted_dsn)
        self.assertIn(":[REDACTED_PASS]@", redacted_dsn)

        sample_pwd = '{"username": "student", "password": "SuperSecretPassword123"}'
        redacted_pwd = redact_sensitive_data(sample_pwd)
        self.assertNotIn("SuperSecretPassword123", redacted_pwd)
        self.assertIn('"password": "[REDACTED_PASSWORD]"', redacted_pwd)

    def test_04_end_to_end_learning_cycle(self):
        """
        Complete end-to-end user lifecycle verification (TEST-03):
        Fetch Challenge -> Submit Code -> Poll Status -> Request AI Hint -> Query RAG -> Check Gamification.
        """
        # 1. Fetch Challenge & verify CODE-06 (no hidden expected outputs)
        req_ch = urllib.request.Request("http://localhost:8000/api/v1/challenges/1")
        with urllib.request.urlopen(req_ch) as resp:
            challenge = json.loads(resp.read().decode())
            self.assertEqual(challenge["id"], 1)
            for tc in challenge.get("test_cases", []):
                if tc.get("is_hidden"):
                    self.assertIsNone(tc.get("expected_output"), "Hidden test outputs must be null")

        # 2. Dispatch Async Submission (CODE-04, HTTP 202)
        submit_payload = json.dumps({
            "challenge_id": 1,
            "code": "def predict_the_winner(nums):\n    return True\n",
            "language": "python"
        }).encode()
        req_sub = urllib.request.Request(
            "http://localhost:8000/api/v1/submissions/",
            data=submit_payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer demo-token"
            },
            method="POST"
        )
        with urllib.request.urlopen(req_sub) as resp:
            self.assertEqual(resp.status, 202)
            sub_data = json.loads(resp.read().decode())
            sub_id = sub_data["submission_id"]
            self.assertIn(sub_data["status"], ["QUEUED", "RUNNING", "PASSED", "FAILED"])

        # 3. Check Submission Status endpoint
        req_st = urllib.request.Request(
            f"http://localhost:8000/api/v1/submissions/{sub_id}/status",
            headers={"Authorization": "Bearer demo-token"}
        )
        with urllib.request.urlopen(req_st) as resp:
            self.assertEqual(resp.status, 200)

        # 4. Request GenAI Coding Mentor Hint (AI-01, AI-02)
        hint_payload = json.dumps({
            "challenge_id": 1,
            "mode": "HINT",
            "code": "def predictTheWinner(nums): return True",
            "language": "python"
        }).encode()
        req_ai = urllib.request.Request(
            "http://localhost:8000/api/v1/ai/mentor",
            data=hint_payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer demo-token"
            },
            method="POST"
        )
        with urllib.request.urlopen(req_ai) as resp:
            self.assertEqual(resp.status, 200)
            ai_data = json.loads(resp.read().decode())
            self.assertEqual(ai_data["mode"], "HINT")
            self.assertIn("content", ai_data)
            self.assertIn("disclaimer", ai_data)

        # 5. Query RAG Learning Assistant (RAG-04)
        rag_payload = json.dumps({
            "question": "What is FastAPI dependency injection?",
            "course_id": 1
        }).encode()
        req_rag = urllib.request.Request(
            "http://localhost:8000/api/v1/ai/learning-assistant",
            data=rag_payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer demo-token"
            },
            method="POST"
        )
        with urllib.request.urlopen(req_rag) as resp:
            self.assertEqual(resp.status, 200)
            rag_data = json.loads(resp.read().decode())
            self.assertTrue(rag_data["sources_found"])
            self.assertGreater(len(rag_data["citations"]), 0)

        # 6. Verify Progress & Badges (GROW-01, GROW-03)
        req_prg = urllib.request.Request(
            "http://localhost:8000/api/v1/progress/",
            headers={"Authorization": "Bearer demo-token"}
        )
        with urllib.request.urlopen(req_prg) as resp:
            self.assertEqual(resp.status, 200)
            prg_data = json.loads(resp.read().decode())
            self.assertIn("total_xp", prg_data)
            self.assertIn("level", prg_data)

        req_bdg = urllib.request.Request(
            "http://localhost:8000/api/v1/badges",
            headers={"Authorization": "Bearer demo-token"}
        )
        with urllib.request.urlopen(req_bdg) as resp:
            self.assertEqual(resp.status, 200)
            badges = json.loads(resp.read().decode())
            self.assertIsInstance(badges, list)
            self.assertGreaterEqual(len(badges), 1)

if __name__ == "__main__":
    unittest.main()
