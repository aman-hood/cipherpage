from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas.course import CourseDetail
from app.database.session import get_db
from app.services.course import course_service
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.get("/", response_model=List[CourseDetail])
def list_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return course_service.get_published_courses(db, skip=skip, limit=limit)

@router.get("/{course_id}", response_model=CourseDetail)
def get_course(course_id: int, db: Session = Depends(get_db)):
    return course_service.get_course_by_id(db, course_id=course_id)

@router.post("/", response_model=CourseDetail, status_code=status.HTTP_201_CREATED)
def create_course(
    course_in: CourseDetail, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["ADMIN", "TEACHER", "INSTRUCTOR"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough privileges")
    return course_service.create_course(db, course_in=course_in)

@router.patch("/{course_id}", response_model=CourseDetail)
def update_course(
    course_id: int, 
    course_in: dict, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["ADMIN", "TEACHER", "INSTRUCTOR"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough privileges")
    return course_service.update_course(db, course_id=course_id, course_in=course_in)

@router.get("/{course_id}/modules")
def get_course_modules(course_id: int, db: Session = Depends(get_db)):
    course = course_service.get_course_by_id(db, course_id=course_id)
    return course.modules
