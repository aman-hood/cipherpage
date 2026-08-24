from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.infrastructure.database import get_db
from app.infrastructure.models import Submission, Challenge
from app.schemas.submission import CodeSubmissionSchema, SubmissionStatusResponse
from app.workers.grader_task import evaluate_student_code

router = APIRouter(prefix="/api/v1/submissions", tags=["Submissions"])

# Mock JWT Dependency
async def get_current_user():
    return {"id": 1, "email": "student@cipherpage.com", "role": "student"}


@router.post("/submit", status_code=status.HTTP_202_ACCEPTED)
async def submit_code(
    payload: CodeSubmissionSchema,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Receives the student's Python code, creates a 'pending' submission record 
    via SQLAlchemy async session, and pushes the job to a Celery worker.
    Returns a 202 Accepted allowing the frontend to show a loading spinner.
    """
    # 1. Verify challenge exists
    challenge_result = await db.execute(select(Challenge).where(Challenge.id == payload.challenge_id))
    challenge = challenge_result.scalars().first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
        
    # 2. Persist a pending submission record in PostgreSQL
    new_submission = Submission(
        student_id=current_user["id"],
        challenge_id=payload.challenge_id,
        submitted_code=payload.source_code,
        status="pending",
        score=0.0,
        passed_tests=0,
        total_tests=0
    )
    db.add(new_submission)
    await db.commit()
    await db.refresh(new_submission)
    
    # 3. Offload execution securely to the Celery worker pool
    # The .delay() pushes this job ID into the Redis broker queue instantly
    evaluate_student_code.delay(new_submission.id)
    
    return {
        "message": "Submission accepted. Grading in progress.",
        "submission_id": new_submission.id
    }


@router.get("/status/{submission_id}", response_model=SubmissionStatusResponse)
async def get_submission_status(
    submission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Polled by the frontend to check if the Celery worker has finished grading.
    Returns the evaluation scorecard (Passed, Failed, Compile Error).
    """
    result = await db.execute(select(Submission).where(Submission.id == submission_id))
    submission = result.scalars().first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
        
    # Security: Ensure students can only poll their own submissions
    if submission.student_id != current_user["id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view this submission")
        
    return SubmissionStatusResponse(
        submission_id=submission.id,
        status=submission.status,
        score=submission.score,
        passed_tests=submission.passed_tests,
        total_tests=submission.total_tests,
        error_logs=getattr(submission, 'error_logs', None)
    )
