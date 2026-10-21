"""
Celery asynchronous tasks for CipherPage.
Handles background grading and safe isolated code execution.
"""
from datetime import datetime
from sqlalchemy.orm import Session
from app.workers.celery_app import celery_app
from app.database.session import SessionLocal
import app.models  # Ensure all models are registered
from app.models.submission import Submission, SubmissionResult
from app.models.challenge import Challenge, TestCase
from app.models.gamification import UserStats, Badge, UserBadge, UserActivity
from app.repositories.progress import progress_repo
from app.integrations.code_runner.runner import code_runner


@celery_app.task(name="evaluate_submission_task")
def evaluate_submission_task(submission_id: str):
    """
    Evaluates a learner's code submission against all configured test cases.
    Performs single compilation for compiled languages (C++, Java).
    If compilation fails, reports COMPILE_ERROR without falsely executing test cases.
    Evaluates every test case, stores results in PostgreSQL, and updates XP/streaks.
    """
    db: Session = SessionLocal()
    try:
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            return {"error": "Submission not found"}

        challenge = db.query(Challenge).filter(Challenge.id == submission.challenge_id).first()
        if not challenge:
            submission.status = "SYSTEM_ERROR"
            submission.error_message = "Challenge not found"
            db.commit()
            return {"error": "Challenge not found"}

        if submission.status in ("PASSED", "FAILED", "COMPILE_ERROR", "RUNTIME_ERROR", "TIME_LIMIT_EXCEEDED", "SECURITY_VIOLATION"):
            return {
                "submission_id": submission.id,
                "status": submission.status,
                "score": submission.score,
                "passed": submission.tests_passed,
                "total": submission.total_tests
            }

        # 1. Update status to RUNNING
        submission.status = "RUNNING"
        db.commit()

        # 2. Retrieve test cases to evaluate
        if submission.evaluation_mode == "custom":
            # Custom input run: single isolated execution
            test_cases = [TestCase(
                challenge_id=challenge.id,
                input_data=submission.custom_input or "",
                expected_output="",
                is_hidden=False,
                order=1
            )]
        else:
            test_case_query = db.query(TestCase).filter(TestCase.challenge_id == challenge.id)
            if submission.evaluation_mode == "run":
                test_case_query = test_case_query.filter(TestCase.is_hidden.is_(False))
            test_cases = test_case_query.order_by(TestCase.order.asc()).all()

        if not test_cases:
            submission.status = "SYSTEM_ERROR"
            submission.error_message = "This challenge has no test cases configured for evaluation."
            submission.total_tests = 0
            db.commit()
            return {"error": submission.error_message}

        total_tests = len(test_cases)

        # 3. Compile or prepare submission ONCE
        prep = code_runner.prepare_submission(
            language=submission.language,
            code=submission.code,
            problem_title=challenge.title
        )

        if not prep.success:
            # If compilation fails, stop immediately! Never pretend test cases ran.
            submission.status = "SECURITY_VIOLATION" if prep.is_security_violation else "COMPILE_ERROR"
            submission.error_message = prep.compile_error
            submission.tests_passed = 0
            submission.total_tests = total_tests
            submission.score = 0.0
            submission.execution_time = 0.0
            submission.memory_usage = 0.0
            db.commit()
            code_runner.cleanup_submission(prep)
            return {
                "submission_id": submission.id,
                "status": submission.status,
                "score": 0.0,
                "passed": 0,
                "total": total_tests,
                "error": prep.compile_error
            }

        # 4. Evaluate each testcase in the isolated runner
        db.query(SubmissionResult).filter(SubmissionResult.submission_id == submission.id).delete()
        db.commit()

        tests_passed = 0
        total_execution_time = 0.0
        max_memory = 0.0
        terminal_status = "PASSED"
        first_error_msg = None

        try:
            for tc in test_cases:
                res = code_runner.execute_test_case(
                    language=submission.language,
                    code=submission.code,
                    input_data=tc.input_data,
                    expected_output=tc.expected_output,
                    prepared=prep,
                    time_limit=challenge.time_limit,
                    memory_limit=challenge.memory_limit
                )

                total_execution_time += res.execution_time
                max_memory = max(max_memory, res.memory_usage)

                # Record individual test case result
                sub_res = SubmissionResult(
                    submission_id=submission.id,
                    test_case_id=tc.id if (hasattr(tc, "id") and tc.id) else None,
                    passed=res.passed,
                    stdout=res.stdout,
                    stderr=res.stderr,
                    execution_time=res.execution_time,
                    memory_usage=res.memory_usage
                )
                db.add(sub_res)

                if res.passed:
                    tests_passed += 1
                else:
                    if terminal_status == "PASSED":
                        terminal_status = res.status
                        first_error_msg = res.error_message or f"Test Case #{tc.order} Failed"
                    if res.status in ("TIME_LIMIT_EXCEEDED", "SECURITY_VIOLATION"):
                        break
        finally:
            code_runner.cleanup_submission(prep)

        # 5. Calculate score and final verdict
        score = (tests_passed / total_tests * 100.0) if total_tests > 0 else 0.0
        submission.status = "PASSED" if (tests_passed == total_tests and total_tests > 0) else terminal_status
        submission.score = round(score, 2)
        submission.tests_passed = tests_passed
        submission.total_tests = total_tests
        submission.execution_time = round(total_execution_time, 4)
        submission.memory_usage = round(max_memory, 2)
        submission.error_message = first_error_msg
        db.commit()

        # 6. If full submit passed all test cases, award XP and progress
        if submission.status == "PASSED" and submission.evaluation_mode == "submit":
            stats = progress_repo.get_user_stats(db, user_id=submission.user_id)
            if stats:
                prior_passed = db.query(Submission).filter(
                    Submission.user_id == submission.user_id,
                    Submission.challenge_id == submission.challenge_id,
                    Submission.status == "PASSED",
                    Submission.evaluation_mode == "submit",
                    Submission.id != submission.id
                ).first()

                if not prior_passed:
                    stats.total_solved += 1
                    diff = challenge.difficulty.upper() if challenge.difficulty else "EASY"
                    if diff == "EASY":
                        stats.easy_solved += 1
                        stats.total_xp += 50
                    elif diff == "MEDIUM":
                        stats.medium_solved += 1
                        stats.total_xp += 100
                    elif diff == "HARD":
                        stats.hard_solved += 1
                        stats.total_xp += 200

                    stats.level = max(1, (stats.total_xp // 100) + 1)

                first_blood = db.query(Badge).filter(Badge.slug == "first-blood").first()
                if first_blood:
                    has_badge = db.query(UserBadge).filter(
                        UserBadge.user_id == submission.user_id,
                        UserBadge.badge_id == first_blood.id
                    ).first()
                    if not has_badge:
                        db.add(UserBadge(user_id=submission.user_id, badge_id=first_blood.id))

                db.add(UserActivity(
                    user_id=submission.user_id,
                    activity_type="SUBMISSION",
                    title=f"Challenge: {challenge.title}",
                    description=f"Passed all 10 test cases for {challenge.title} in {submission.language.upper()}",
                    action_label="Passed"
                ))

                db.commit()

        return {
            "submission_id": submission.id,
            "status": submission.status,
            "score": submission.score,
            "passed": tests_passed,
            "total": total_tests
        }
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()
