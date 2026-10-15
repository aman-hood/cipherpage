from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.progress import progress_service
from app.schemas.progress import ProgressUpdate, OverallProgress
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/progress", tags=["Progress"])

@router.get("/", response_model=OverallProgress)
def get_overall_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve overall user learning progress and gamification statistics."""
    return progress_service.get_progress(db, user=current_user)

@router.post("/lecture")
def update_lecture_progress(
    update: ProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update progress for a specific lecture and calculate XP."""
    return progress_service.update_lecture_progress(db, user=current_user, update=update)
