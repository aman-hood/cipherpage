import unittest
from app.database.session import SessionLocal
from app.models.user import User
from app.models.ai import AIUsageRecord
from app.schemas.ai import AIMentorRequest
from app.services.ai_mentor import ai_mentor_service, DAILY_AI_QUOTA_LIMIT

class TestPhase3GenAIMentor(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.user = self.db.query(User).filter(User.email == "demo@cipherpage.com").first()
        if self.user:
            count = self.db.query(AIUsageRecord).filter(AIUsageRecord.user_id == self.user.id).count()
            if count >= 40:
                self.db.query(AIUsageRecord).filter(AIUsageRecord.user_id == self.user.id).delete()
                self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_01_quota_initial_state(self):
        """Verify daily quota status reporting (AI-07)."""
        status = ai_mentor_service.get_quota_status(self.db, user=self.user)
        self.assertEqual(status.daily_limit, DAILY_AI_QUOTA_LIMIT)
        self.assertGreaterEqual(status.remaining_quota, 0)

    def test_02_hint_mode_socratic_guidance(self):
        """Verify Hint mode provides Socratic guidance without spoiling full solution (AI-02)."""
        req = AIMentorRequest(
            challenge_id=1,
            mode="HINT",
            code="def predictTheWinner(nums):\n    pass\n",
            language="python",
            request_full_solution=False
        )
        resp = ai_mentor_service.process_mentor_request(self.db, user=self.user, req=req)
        self.assertEqual(resp.mode, "HINT")
        self.assertIn("Hint", resp.content)
        # Should NOT contain full solution class implementation by default
        self.assertNotIn("class Solution:", resp.content)
        self.assertIn("disclaimer", resp.model_dump())

    def test_03_hint_mode_reveal_full_solution_when_asked(self):
        """Verify Hint mode reveals complete solution only when learner explicitly asks (AI-02)."""
        req = AIMentorRequest(
            challenge_id=1,
            mode="HINT",
            code="def predictTheWinner(nums):\n    pass\n",
            language="python",
            request_full_solution=True
        )
        resp = ai_mentor_service.process_mentor_request(self.db, user=self.user, req=req)
        self.assertEqual(resp.mode, "HINT")
        self.assertIn("Complete Solution", resp.content)
        self.assertIn("class Solution", resp.content)

    def test_04_debug_mode(self):
        """Verify Debug mode analyzes code and errors (AI-03)."""
        req = AIMentorRequest(
            challenge_id=1,
            mode="DEBUG",
            code="def predictTheWinner(nums):\n    return nums[0] > nums[-1]\n",
            language="python",
            error_output="AssertionError: Expected true but got false on [1, 5, 233, 7]"
        )
        resp = ai_mentor_service.process_mentor_request(self.db, user=self.user, req=req)
        self.assertEqual(resp.mode, "DEBUG")
        self.assertIn("Debug", resp.content)

    def test_05_explain_mode(self):
        """Verify Explain mode provides stepwise explanation (AI-04)."""
        req = AIMentorRequest(
            challenge_id=1,
            mode="EXPLAIN",
            code="def predictTheWinner(nums):\n    dp = list(nums)\n    # ...\n",
            language="python"
        )
        resp = ai_mentor_service.process_mentor_request(self.db, user=self.user, req=req)
        self.assertEqual(resp.mode, "EXPLAIN")
        self.assertIn("Explanation", resp.content)

    def test_06_complexity_mode(self):
        """Verify Complexity mode provides time and space Big-O analysis (AI-04)."""
        req = AIMentorRequest(
            challenge_id=1,
            mode="COMPLEXITY",
            code="def predictTheWinner(nums):\n    n = len(nums)\n    # nested loop\n",
            language="python"
        )
        resp = ai_mentor_service.process_mentor_request(self.db, user=self.user, req=req)
        self.assertEqual(resp.mode, "COMPLEXITY")
        self.assertIn("Complexity", resp.content)
        self.assertTrue("O(N" in resp.content or "Time Complexity" in resp.content)

    def test_07_usage_record_logged(self):
        """Verify AI usage records are persisted to DB (AI-07)."""
        records = self.db.query(AIUsageRecord).filter(AIUsageRecord.user_id == self.user.id).all()
        self.assertGreater(len(records), 0, "Usage records should be logged in database")

if __name__ == "__main__":
    unittest.main()
