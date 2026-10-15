from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.submission import submission_repo
from app.repositories.challenge import challenge_repo
from app.models.submission import Submission, SubmissionResult
from app.models.user import User
from app.schemas.submission import CodeSubmission, EvaluationResult, SubmissionResultDetail

class SubmissionService:
    @staticmethod
    def create_submission(db: Session, submission_in: CodeSubmission, current_user: User) -> Submission:
        challenge = challenge_repo.get(db, id=submission_in.challenge_id)
        if not challenge:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")

        total_tests = len(challenge.test_cases) if challenge.test_cases else 0

        submission = Submission(
            user_id=current_user.id,
            challenge_id=submission_in.challenge_id,
            code=submission_in.code,
            language=submission_in.language,
            status="QUEUED",
            score=0.0,
            tests_passed=0,
            total_tests=total_tests,
            execution_time=0.0,
            memory_usage=0.0
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)

        # Dispatch asynchronous evaluation to Celery worker (CODE-04, API-04)
        try:
            from app.workers.tasks import evaluate_submission_task
            evaluate_submission_task.delay(submission.id)
        except Exception as e:
            # If celery broker is unavailable, run synchronously as graceful fallback
            try:
                from app.workers.tasks import evaluate_submission_task
                evaluate_submission_task(submission.id)
                db.refresh(submission)
            except Exception:
                pass

        return submission

    @staticmethod
    def get_challenge_submissions(db: Session, user_id: int, challenge_id: int) -> List[EvaluationResult]:
        submissions = submission_repo.get_user_submissions(db, user_id=user_id, challenge_id=challenge_id)
        return [SubmissionService.get_submission_detail(db, submission_id=s.id) for s in submissions]

    @staticmethod
    def get_submission_detail(db: Session, submission_id: str) -> EvaluationResult:
        submission = submission_repo.get_by_submission_id(db, submission_id=submission_id)
        if not submission:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")

        results_detail = [
            SubmissionResultDetail(
                id=r.id,
                test_case_id=r.test_case_id,
                passed=r.passed,
                stdout=r.stdout,
                stderr=r.stderr,
                execution_time=r.execution_time,
                memory_usage=r.memory_usage
            )
            for r in submission.results
        ]

        return EvaluationResult(
            submission_id=submission.id,
            challenge_id=submission.challenge_id,
            status=submission.status,
            score=submission.score,
            tests_passed=submission.tests_passed,
            total_tests=submission.total_tests,
            execution_time=submission.execution_time,
            memory_usage=submission.memory_usage,
            error_message=submission.error_message,
            created_at=submission.created_at,
            results=results_detail
        )

submission_service = SubmissionService()
