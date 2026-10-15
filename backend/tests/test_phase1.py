import unittest
import json
import urllib.request
import urllib.error
from app.database.session import SessionLocal
from app.models.user import User
from app.models.challenge import Challenge, TestCase
from app.models.submission import Submission
from app.models.gamification import Badge, UserStats
from app.services.challenge import challenge_service

class TestPhase1Core(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_01_database_models_exist(self):
        """Verify models can be queried and have expected records."""
        user = self.db.query(User).filter(User.email == "demo@cipherpage.com").first()
        self.assertIsNotNone(user, "Demo user should exist in the database")

        challenges = self.db.query(Challenge).all()
        self.assertGreaterEqual(len(challenges), 2, "At least 2 seeded challenges should exist")

        badges = self.db.query(Badge).all()
        self.assertGreaterEqual(len(badges), 4, "Seeded badges should exist")

        stats = self.db.query(UserStats).filter(UserStats.user_id == user.id).first()
        self.assertIsNotNone(stats, "User stats should exist for demo user")

    def test_02_hidden_test_cases_sanitized(self):
        """Verify CODE-06: Never return hidden test cases or expected answers to client."""
        challenge = self.db.query(Challenge).filter(Challenge.slug == "predict-the-winner").first()
        self.assertIsNotNone(challenge)

        detail = challenge_service.get_challenge_by_id(self.db, challenge_id=challenge.id, sanitize_hidden=True)
        self.assertIsNotNone(detail.test_cases)
        
        hidden_cases = [tc for tc in detail.test_cases if tc.is_hidden]
        self.assertGreater(len(hidden_cases), 0, "Should have hidden test cases")
        for tc in hidden_cases:
            self.assertIsNone(tc.expected_output, "Hidden test cases must have null expected_output")

    def test_03_api_health_endpoint(self):
        """Verify /health returns HTTP 200 with status ok."""
        with urllib.request.urlopen("http://localhost:8000/health") as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode())
            self.assertEqual(data.get("status"), "ok")

    def test_04_api_challenges_endpoint(self):
        """Verify /api/v1/challenges/ returns challenge list."""
        with urllib.request.urlopen("http://localhost:8000/api/v1/challenges/") as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode())
            self.assertIsInstance(data, list)
            self.assertGreaterEqual(len(data), 2)
            self.assertEqual(data[0]["slug"], "predict-the-winner")

    def test_05_protected_endpoint_rejects_unauthenticated(self):
        """Verify AC-01: Protected endpoints reject unauthenticated requests with 401."""
        req = urllib.request.Request(
            "http://localhost:8000/api/v1/submissions/",
            data=json.dumps({"challenge_id": 1, "code": "print(1)", "language": "python"}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 401)

if __name__ == "__main__":
    unittest.main()
