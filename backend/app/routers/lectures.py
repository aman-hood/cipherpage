from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.course import Lecture
from app.schemas.course import LectureBase
from app.dependencies.auth import ensure_course_access, get_current_user
from app.models.user import User

router = APIRouter(prefix="/lectures", tags=["Lectures"])

@router.get("/{lecture_id}", response_model=LectureBase)
def get_lecture(
    lecture_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve lecture metadata dynamically from database."""
    lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
    if not lecture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lecture with ID {lecture_id} not found"
        )
    ensure_course_access(db, current_user, lecture.module.course)
    return LectureBase(
        title=lecture.title,
        duration=lecture.duration,
        video_url=lecture.video_url
    )
