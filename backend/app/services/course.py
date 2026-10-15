from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.course import course_repo
from app.models.course import Course
from app.schemas.course import CourseDetail

class CourseService:
    @staticmethod
    def get_published_courses(db: Session, skip: int = 0, limit: int = 100) -> List[Course]:
        return course_repo.get_published(db, skip=skip, limit=limit)
        
    @staticmethod
    def get_course_by_id(db: Session, course_id: int) -> Course:
        course = course_repo.get(db, id=course_id)
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        return course

    @staticmethod
    def create_course(db: Session, course_in: CourseDetail) -> Course:
        existing_course = course_repo.get_by_slug(db, slug=course_in.slug)
        if existing_course:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Course with this slug already exists")
        return course_repo.create(db, obj_in=course_in)

    @staticmethod
    def update_course(db: Session, course_id: int, course_in: dict) -> Course:
        course = course_repo.get(db, id=course_id)
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        for field, val in course_in.items():
            if hasattr(course, field) and val is not None and field != "id":
                setattr(course, field, val)
        db.commit()
        db.refresh(course)
        return course

course_service = CourseService()
