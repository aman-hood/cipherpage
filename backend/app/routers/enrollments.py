from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.enrollment import enrollment_service
from app.schemas.enrollment import EnrollmentDetail
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])

@router.post("/", response_model=EnrollmentDetail, status_code=status.HTTP_201_CREATED)
def enroll_in_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Enroll the current authenticated user in a course."""
    return enrollment_service.enroll_user(db, course_id=course_id, user=current_user)

@router.get("/me/courses", response_model=List[EnrollmentDetail])
def get_my_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all courses the current user is enrolled in."""
    return enrollment_service.get_my_courses(db, user=current_user)
