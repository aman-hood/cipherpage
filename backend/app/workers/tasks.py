"""
Celery asynchronous tasks for CipherPage.
Handles background grading and safe isolated code execution.
"""
from datetime import datetime
from sqlalchemy.orm import Session
from app.workers.celery_app import celery_app
from app.database.session import SessionLocal
import app.models # Ensure all models are registered
from app.models.submission import Submission, SubmissionResult
from app.models.challenge import Challenge, TestCase
from app.models.gamification import UserStats, Badge, UserBadge
from app.repositories.progress import progress_repo
from app.integrations.code_runner.runner import code_runner

@celery_app.task(name="evaluate_submission_task")
def evaluate_submission_task(submission_id: str):
    """
    Asynchronous Celery task that grades a learner's code submission against
    all public and hidden test cases in isolation.
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

        # 1. Update status to RUNNING
        submission.status = "RUNNING"
        db.commit()

        test_cases = db.query(TestCase).filter(TestCase.challenge_id == challenge.id).order_by(TestCase.order.asc()).all()
        total_tests = len(test_cases)
        tests_passed = 0
        total_execution_time = 0.0
        max_memory = 0.0
        terminal_status = "PASSED"
        first_error_msg = None

        # 2. Execute each test case
        for tc in test_cases:
            res = code_runner.evaluate(
                language=submission.language,
                code=submission.code,
                input_data=tc.input_data,
                expected_output=tc.expected_output,
                time_limit=challenge.time_limit,
                memory_limit=challenge.memory_limit
            )

            total_execution_time += res.execution_time
            max_memory = max(max_memory, res.memory_usage)

            # Record result
            sub_res = SubmissionResult(
                submission_id=submission.id,
                test_case_id=tc.id,
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
                    first_error_msg = res.error_message

        # 3. Update final submission state
        score = (tests_passed / total_tests * 100.0) if total_tests > 0 else 0.0
        submission.status = "PASSED" if (tests_passed == total_tests and total_tests > 0) else terminal_status
        submission.score = round(score, 2)
        submission.tests_passed = tests_passed
        submission.total_tests = total_tests
        submission.execution_time = round(total_execution_time, 4)
        submission.memory_usage = round(max_memory, 2)
        submission.error_message = first_error_msg
        db.commit()

        # 4. If submission passed, award XP and progress (GROW-02, GROW-03)
        if submission.status == "PASSED":
            stats = progress_repo.get_user_stats(db, user_id=submission.user_id)
            if stats:
                # Anti-farming check: only award XP if this is the user's first time passing this challenge
                prior_passed = db.query(Submission).filter(
                    Submission.user_id == submission.user_id,
                    Submission.challenge_id == submission.challenge_id,
                    Submission.status == "PASSED",
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

                # Check "first-blood" badge
                first_blood = db.query(Badge).filter(Badge.slug == "first-blood").first()
                if first_blood:
                    has_badge = db.query(UserBadge).filter(
                        UserBadge.user_id == submission.user_id,
                        UserBadge.badge_id == first_blood.id
                    ).first()
                    if not has_badge:
                        db.add(UserBadge(user_id=submission.user_id, badge_id=first_blood.id))

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
