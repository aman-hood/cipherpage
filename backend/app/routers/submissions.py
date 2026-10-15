from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.submission import submission_service
from app.repositories.submission import submission_repo
from app.schemas.submission import CodeSubmission, EvaluationResult, SubmissionStatusResponse
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/submissions", tags=["Code Submissions"])

@router.post("/", response_model=EvaluationResult, status_code=status.HTTP_202_ACCEPTED)
def submit_code(
    submission: CodeSubmission,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submits learner code for evaluation.
    Creates a submission with status QUEUED and returns the submission ID (HTTP 202).
    """
    new_sub = submission_service.create_submission(db, submission_in=submission, current_user=current_user)
    return submission_service.get_submission_detail(db, submission_id=new_sub.id)

@router.get("/{submission_id}", response_model=EvaluationResult)
def get_submission(
    submission_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve full evaluation result for a submission (IDOR protected)."""
    raw_sub = submission_repo.get_by_submission_id(db, submission_id=submission_id)
    if not raw_sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    if raw_sub.user_id != current_user.id and current_user.role not in ["ADMIN", "TEACHER"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden to this submission")
    return submission_service.get_submission_detail(db, submission_id=submission_id)

@router.get("/{submission_id}/status", response_model=SubmissionStatusResponse)
def get_submission_status(
    submission_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lightweight polling endpoint to check if evaluation is complete (IDOR protected)."""
    raw_sub = submission_repo.get_by_submission_id(db, submission_id=submission_id)
    if not raw_sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    if raw_sub.user_id != current_user.id and current_user.role not in ["ADMIN", "TEACHER"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden to this submission")
    sub_detail = submission_service.get_submission_detail(db, submission_id=submission_id)
    return SubmissionStatusResponse(
        submission_id=sub_detail.submission_id,
        status=sub_detail.status,
        tests_passed=sub_detail.tests_passed,
        total_tests=sub_detail.total_tests,
        score=sub_detail.score
    )

@router.get("/history/{challenge_id}", response_model=list[EvaluationResult])
def get_submission_history(
    challenge_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve submission history for the authenticated user and given challenge."""
    return submission_service.get_challenge_submissions(db, user_id=current_user.id, challenge_id=challenge_id)

