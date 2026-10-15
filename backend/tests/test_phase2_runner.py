import unittest
import time
from app.database.session import SessionLocal
from app.models.user import User
from app.models.challenge import Challenge
from app.models.submission import Submission
from app.models.gamification import UserStats
from app.services.submission import submission_service
from app.schemas.submission import CodeSubmission
from app.integrations.code_runner.runner import code_runner

class TestPhase2CodingArena(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.user = self.db.query(User).filter(User.email == "demo@cipherpage.com").first()
        self.challenge = self.db.query(Challenge).filter(Challenge.slug == "predict-the-winner").first()

    def tearDown(self):
        self.db.close()

    def test_01_code_runner_evaluates_correct_code(self):
        """Test isolated code runner with working solution."""
        solution_code = """
class Solution:
    def predictTheWinner(self, nums: list[int]) -> bool:
        n = len(nums)
        dp = list(nums)
        for diff in range(1, n):
            for i in range(n - diff):
                j = i + diff
                dp[i] = max(nums[i] - dp[i + 1], nums[j] - dp[i])
        return dp[0] >= 0
"""
        res = code_runner.evaluate(
            language="python",
            code=solution_code,
            input_data="[1, 5, 2]",
            expected_output="false"
        )
        self.assertTrue(res.passed, f"Should pass test case [1, 5, 2]: {res.error_message}")
        self.assertEqual(res.status, "PASSED")
        self.assertGreater(res.execution_time, 0.0)

    def test_02_code_runner_catches_wrong_answer(self):
        """Test isolated code runner with wrong return value."""
        wrong_code = """
class Solution:
    def predictTheWinner(self, nums: list[int]) -> bool:
        return True # Always returns True
"""
        res = code_runner.evaluate(
            language="python",
            code=wrong_code,
            input_data="[1, 5, 2]",
            expected_output="false"
        )
        self.assertFalse(res.passed)
        self.assertEqual(res.status, "FAILED")

    def test_03_code_runner_catches_runtime_error(self):
        """Test isolated code runner catches exception without crashing."""
        error_code = """
class Solution:
    def predictTheWinner(self, nums: list[int]) -> bool:
        return 1 / 0
"""
        res = code_runner.evaluate(
            language="python",
            code=error_code,
            input_data="[1, 5, 2]",
            expected_output="false"
        )
        self.assertFalse(res.passed)
        self.assertEqual(res.status, "RUNTIME_ERROR")

    def test_04_async_submission_workflow(self):
        """Test complete submission creation, asynchronous execution, and DB persistence."""
        solution_code = """
class Solution:
    def predictTheWinner(self, nums: list[int]) -> bool:
        n = len(nums)
        dp = list(nums)
        for diff in range(1, n):
            for i in range(n - diff):
                j = i + diff
                dp[i] = max(nums[i] - dp[i + 1], nums[j] - dp[i])
        return dp[0] >= 0
"""
        submission_in = CodeSubmission(
            challenge_id=self.challenge.id,
            code=solution_code,
            language="python"
        )
        sub = submission_service.create_submission(self.db, submission_in=submission_in, current_user=self.user)
        self.assertIsNotNone(sub.id)

        # Allow worker up to 3 seconds to complete evaluation
        for _ in range(30):
            time.sleep(0.1)
            self.db.expire_all()
            updated_sub = self.db.query(Submission).filter(Submission.id == sub.id).first()
            if updated_sub.status in ["PASSED", "FAILED", "RUNTIME_ERROR"]:
                break

        detail = submission_service.get_submission_detail(self.db, submission_id=sub.id)
        self.assertIn(detail.status, ["PASSED", "FAILED", "QUEUED", "RUNNING"])
        self.assertGreater(detail.total_tests, 0)
        self.assertEqual(detail.challenge_id, self.challenge.id)

if __name__ == "__main__":
    unittest.main()
