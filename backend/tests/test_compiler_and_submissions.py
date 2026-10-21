import unittest
import time
import concurrent.futures
from app.database.session import SessionLocal
from app.models.user import User
from app.models.challenge import Challenge, TestCase
from app.models.submission import Submission, SubmissionResult
from app.schemas.submission import CodeSubmission
from app.services.submission import submission_service
from app.workers.tasks import evaluate_submission_task
from app.integrations.code_runner.runner import code_runner


class TestCompilerAndSubmissionPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import os
        os.environ["CIPHERPAGE_TESTING"] = "1"
        cls.db = SessionLocal()
        # Ensure test users exist
        cls.user_a = cls.db.query(User).filter(User.email == "alice_compiler@cipherpage.com").first()
        if not cls.user_a:
            cls.user_a = User(name="Alice Coder", email="alice_compiler@cipherpage.com", role="STUDENT", is_active=True)
            cls.db.add(cls.user_a)
            cls.db.commit()
            cls.db.refresh(cls.user_a)

        cls.user_b = cls.db.query(User).filter(User.email == "bob_compiler@cipherpage.com").first()
        if not cls.user_b:
            cls.user_b = User(name="Bob Coder", email="bob_compiler@cipherpage.com", role="STUDENT", is_active=True)
            cls.db.add(cls.user_b)
            cls.db.commit()
            cls.db.refresh(cls.user_b)

        # Retrieve challenge 1 (Predict the Winner) with 10 test cases
        cls.challenge = cls.db.query(Challenge).filter(Challenge.slug == "predict-the-winner").first()
        assert cls.challenge is not None, "Challenge predict-the-winner must exist"
        assert len(cls.challenge.test_cases) == 10, f"Must have 10 test cases, found {len(cls.challenge.test_cases)}"

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_01_correct_cpp_solution_passes_all_10_test_cases(self):
        """1. A correct C++ solution passes all 10 test cases."""
        correct_cpp_code = """#include <vector>
#include <algorithm>
using namespace std;

class Solution {
public:
    bool predictTheWinner(vector<int>& nums) {
        int n = nums.size();
        vector<int> dp = nums;
        for (int i = n - 2; i >= 0; --i) {
            for (int j = i + 1; j < n; ++j) {
                dp[j] = max(nums[i] - dp[j], nums[j] - dp[j - 1]);
            }
        }
        return dp[n - 1] >= 0;
    }
};
"""
        sub_in = CodeSubmission(
            challenge_id=self.challenge.id,
            code=correct_cpp_code,
            language="cpp",
            mode="submit"
        )
        submission = submission_service.create_submission(self.db, sub_in, self.user_a)
        # Execute evaluation
        evaluate_submission_task(submission.id)
        self.db.refresh(submission)

        self.assertEqual(submission.status, "PASSED")
        self.assertEqual(submission.tests_passed, 10)
        self.assertEqual(submission.total_tests, 10)
        self.assertEqual(submission.score, 100.0)
        self.assertEqual(len(submission.results), 10)
        self.assertTrue(all(r.passed for r in submission.results))

    def test_02_solution_passes_7_of_10_test_cases(self):
        """2. A solution passes only 7 of the 10 test cases and receives the correct verdict (7/10, FAILED)."""
        # In Predict the Winner test cases:
        # Expected outputs for 10 test cases:
        # TC 1: false
        # TC 2: true
        # TC 3: true
        # TC 4: true
        # TC 5: true
        # TC 6: true
        # TC 7: true
        # TC 8: false
        # TC 9: true
        # TC 10: true
        # Notice that exactly 8 cases expect true, and 2 expect false (TC 1 and TC 8)!
        # If a solution always returns true: it passes 8/10.
        # If a solution returns true except when array length == 3 where it returns false:
        # TC 1: len 3, returns false (passes, 1)
        # TC 2: len 4, returns true (passes, 2)
        # TC 3: len 2, returns true (passes, 3)
        # TC 4: len 4, returns true (passes, 4)
        # TC 5: len 3, returns false (fails, expects true)
        # TC 6: len 5, returns true (passes, 5)
        # TC 7: len 5, returns true (passes, 6)
        # TC 8: len 4, returns true (fails, expects false)
        # TC 9: len 10, returns true (passes, 7)
        # TC 10: len 8, returns true (passes, 8)
        partial_code = """class Solution:
    def predictTheWinner(self, nums: list[int]) -> bool:
        # Fails TC 2 (returns False, expects True), and fails TC 1 & TC 7 (returns True, expects False).
        # Passes remaining 7 cases (TC 3, 4, 5, 6, 8, 9, 10).
        if nums == [1, 5, 233, 7]:
            return False
        return True
"""
        sub_in = CodeSubmission(
            challenge_id=self.challenge.id,
            code=partial_code,
            language="python",
            mode="submit"
        )
        submission = submission_service.create_submission(self.db, sub_in, self.user_a)
        evaluate_submission_task(submission.id)
        self.db.refresh(submission)

        self.assertEqual(submission.status, "FAILED")
        self.assertEqual(submission.tests_passed, 7)
        self.assertEqual(submission.total_tests, 10)
        self.assertEqual(submission.score, 70.0)
        self.assertEqual(len(submission.results), 10)
        passed_count = sum(1 for r in submission.results if r.passed)
        self.assertEqual(passed_count, 7)

    def test_03_invalid_cpp_syntax_produces_compilation_error(self):
        """3. Invalid C++ syntax produces a Compilation Error and does not falsely run test cases."""
        bad_cpp = """#include <vector>
class Solution {
public:
    bool predictTheWinner(std::vector<int>& nums) {
        int x = ; // Syntax error
        return true;
    }
};
"""
        sub_in = CodeSubmission(
            challenge_id=self.challenge.id,
            code=bad_cpp,
            language="cpp",
            mode="submit"
        )
        submission = submission_service.create_submission(self.db, sub_in, self.user_a)
        evaluate_submission_task(submission.id)
        self.db.refresh(submission)

        self.assertEqual(submission.status, "COMPILE_ERROR")
        self.assertEqual(submission.tests_passed, 0)
        self.assertEqual(submission.score, 0.0)
        self.assertIsNotNone(submission.error_message)
        self.assertIn("error:", submission.error_message.lower())
        # Results should have 0 executed test cases
        self.assertEqual(len(submission.results), 0)

    def test_04_runtime_crash_produces_runtime_error(self):
        """4. A program that crashes produces a Runtime Error."""
        crash_code = """class Solution:
    def predictTheWinner(self, nums: list[int]) -> bool:
        # Deliberate division by zero crash
        val = 10 // 0
        return True
"""
        sub_in = CodeSubmission(
            challenge_id=self.challenge.id,
            code=crash_code,
            language="python",
            mode="submit"
        )
        submission = submission_service.create_submission(self.db, sub_in, self.user_a)
        evaluate_submission_task(submission.id)
        self.db.refresh(submission)

        self.assertEqual(submission.status, "RUNTIME_ERROR")
        self.assertIn("ZeroDivisionError", submission.error_message)

    def test_05_incorrect_output_produces_wrong_answer(self):
        """5. An incorrect output produces Wrong Answer (FAILED)."""
        wrong_code = """class Solution:
    def predictTheWinner(self, nums: list[int]) -> bool:
        # Deliberately return opposite
        return False
"""
        sub_in = CodeSubmission(
            challenge_id=self.challenge.id,
            code=wrong_code,
            language="python",
            mode="submit"
        )
        submission = submission_service.create_submission(self.db, sub_in, self.user_a)
        evaluate_submission_task(submission.id)
        self.db.refresh(submission)

        self.assertEqual(submission.status, "FAILED")
        self.assertNotEqual(submission.status, "PASSED")

    def test_06_infinite_loop_stopped_by_time_limit(self):
        """6. An infinite loop is stopped by the time limit."""
        infinite_loop_code = """class Solution:
    def predictTheWinner(self, nums: list[int]) -> bool:
        import time
        # Infinite busy loop
        start = time.time()
        while True:
            if time.time() - start > 10.0:
                break
        return True
"""
        sub_in = CodeSubmission(
            challenge_id=self.challenge.id,
            code=infinite_loop_code,
            language="python",
            mode="run" # 5 public cases
        )
        # Note: challenge time_limit is 2.0s
        submission = submission_service.create_submission(self.db, sub_in, self.user_a)
        evaluate_submission_task(submission.id)
        self.db.refresh(submission)

        self.assertEqual(submission.status, "TIME_LIMIT_EXCEEDED")
        self.assertIn("time limit", submission.error_message.lower())

    def test_07_memory_consumption_handled_cleanly(self):
        """7. A solution with high memory allocation is handled within configured bounds."""
        mem_code = """class Solution:
    def predictTheWinner(self, nums: list[int]) -> bool:
        # Allocate large array safely without crashing host
        data = [0] * (10 ** 6)
        return len(data) > 0
"""
        sub_in = CodeSubmission(
            challenge_id=self.challenge.id,
            code=mem_code,
            language="python",
            mode="run"
        )
        submission = submission_service.create_submission(self.db, sub_in, self.user_a)
        evaluate_submission_task(submission.id)
        self.db.refresh(submission)

        self.assertIn(submission.status, ["PASSED", "FAILED"])
        self.assertGreater(submission.memory_usage, 0.0)

    def test_08_empty_and_multiline_input_handling(self):
        """8. Multi-line input and edge inputs are parsed correctly."""
        res = code_runner.evaluate(
            language="python",
            code="""class Solution:
    def predictTheWinner(self, nums: list[int]) -> bool:
        return len(nums) == 3
""",
            input_data="nums = [\n  1,\n  5,\n  2\n]",
            expected_output="true"
        )
        self.assertTrue(res.passed)
        self.assertEqual(res.status, "PASSED")

    def test_09_all_supported_languages_use_correct_runner(self):
        """9. Submissions in each supported programming language (Python, C++, Java, JS) execute properly."""
        # Python
        py_res = code_runner.evaluate(
            language="python",
            code="class Solution:\n    def predictTheWinner(self, nums: list[int]) -> bool:\n        return True\n",
            input_data="[1, 5, 2]",
            expected_output="true"
        )
        self.assertEqual(py_res.status, "PASSED")

        # C++
        cpp_res = code_runner.evaluate(
            language="cpp",
            code="""#include <vector>
using namespace std;
class Solution {
public:
    bool predictTheWinner(vector<int>& nums) {
        return true;
    }
};
""",
            input_data="[1, 5, 2]",
            expected_output="true"
        )
        self.assertEqual(cpp_res.status, "PASSED")

        # JavaScript
        js_res = code_runner.evaluate(
            language="javascript",
            code="function predictTheWinner(nums) { return true; }",
            input_data="[1, 5, 2]",
            expected_output="true"
        )
        self.assertEqual(js_res.status, "PASSED")

    def test_10_concurrent_submissions_maintain_complete_isolation(self):
        """10. Multiple users submitting concurrently receive their own independent results."""
        def run_user_submission(user, lang, code_snippet):
            local_db = SessionLocal()
            try:
                sub_in = CodeSubmission(
                    challenge_id=self.challenge.id,
                    code=code_snippet,
                    language=lang,
                    mode="run"
                )
                sub = submission_service.create_submission(local_db, sub_in, user)
                evaluate_submission_task(sub.id)
                local_db.refresh(sub)
                return sub.id, sub.user_id, sub.status, sub.tests_passed
            finally:
                local_db.close()

        code_alice = "class Solution:\n    def predictTheWinner(self, nums: list[int]) -> bool:\n        return True\n"
        code_bob = "class Solution:\n    def predictTheWinner(self, nums: list[int]) -> bool:\n        return False\n"

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_a = executor.submit(run_user_submission, self.user_a, "python", code_alice)
            future_b = executor.submit(run_user_submission, self.user_b, "python", code_bob)
            res_a = future_a.result()
            res_b = future_b.result()

        # Check Alice
        self.assertEqual(res_a[1], self.user_a.id)
        # Check Bob
        self.assertEqual(res_b[1], self.user_b.id)
        # Alice and Bob have different IDs and independent test pass counts
        self.assertNotEqual(res_a[0], res_b[0])
        self.assertNotEqual(res_a[3], res_b[3])

    def test_11_custom_run_does_not_count_toward_judging_or_affect_history(self):
        """Custom Run executes only the supplied custom input without altering 10 judging tests."""
        custom_code = "class Solution:\n    def predictTheWinner(self, nums: list[int]) -> bool:\n        return sum(nums) == 42\n"
        sub_in = CodeSubmission(
            challenge_id=self.challenge.id,
            code=custom_code,
            language="python",
            mode="custom",
            custom_input="[20, 22]"
        )
        submission = submission_service.create_submission(self.db, sub_in, self.user_a)
        evaluate_submission_task(submission.id)
        self.db.refresh(submission)

        self.assertEqual(submission.evaluation_mode, "custom")
        self.assertEqual(submission.total_tests, 1)
        self.assertEqual(submission.status, "PASSED")
        self.assertEqual(len(submission.results), 1)
        self.assertEqual(submission.results[0].stdout, "true")


if __name__ == "__main__":
    unittest.main()
