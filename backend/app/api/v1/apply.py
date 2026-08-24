from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import get_db
from app.infrastructure.models import Submission
from app.domain.schemas import CodeSubmission, CodeSubmissionResponse
from app.worker.tasks import evaluate_student_code

router = APIRouter(prefix="/apply", tags=["LAG Apply"])

# Mock JWT Dependency
async def get_current_user():
    return {"id": 1, "email": "student@cipherpage.com", "role": "student"}

@router.post("/submit", response_model=CodeSubmissionResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_code(
    payload: CodeSubmission,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Receives a student's code payload from the 'Apply' interface, 
    persists it, and offloads heavy evaluation to the Celery worker queue.
    """
    # 1. Create a pending submission record in DB
    new_submission = Submission(
        student_id=current_user["id"],
        challenge_id=payload.challenge_id,
        submitted_code=payload.submitted_code,
        status="pending"
    )
    db.add(new_submission)
    await db.commit()
    await db.refresh(new_submission)
    
    # 2. Trigger Celery task asynchronously using .delay()
    # This places the job in Redis, freeing up FastAPI immediately!
    evaluate_student_code.delay(new_submission.id)
    
    return CodeSubmissionResponse(
        submission_id=new_submission.id,
        message="Your code has been submitted successfully and is being graded in the background."
    )
