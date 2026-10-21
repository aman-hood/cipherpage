import os
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

        challenge_test_cases = sorted(challenge.test_cases or [], key=lambda test_case: test_case.order)
        if submission_in.mode == "run":
            challenge_test_cases = [test_case for test_case in challenge_test_cases if not test_case.is_hidden]
        elif submission_in.mode == "custom":
            challenge_test_cases = []

        total_tests = 1 if submission_in.mode == "custom" else len(challenge_test_cases)
        if total_tests == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This challenge has no test cases available for this operation",
            )

        submission = Submission(
            user_id=current_user.id,
            challenge_id=submission_in.challenge_id,
            code=submission_in.code,
            language=submission_in.language,
            evaluation_mode=submission_in.mode,
            custom_input=submission_in.custom_input,
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

        # Dispatch evaluation: attempt fast async celery, fallback to sync execution
        if os.environ.get("CIPHERPAGE_TESTING") != "1":
            try:
                from app.workers.tasks import evaluate_submission_task
                evaluate_submission_task.apply_async(args=[submission.id])
            except Exception:
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
                test_case_order=r.test_case.order if r.test_case else 1,
                passed=r.passed,
                stdout=r.stdout,
                stderr=r.stderr,
                execution_time=r.execution_time,
                memory_usage=r.memory_usage,
                status="PASSED" if r.passed else "FAILED"
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
