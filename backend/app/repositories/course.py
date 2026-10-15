from typing import Optional, List
from sqlalchemy.orm import Session
from app.repositories.base import CRUDBase
from app.models.course import Course, Module, Lecture
from app.schemas.course import CourseDetail

class CourseRepository(CRUDBase[Course, CourseDetail, CourseDetail]):
    def get_by_slug(self, db: Session, *, slug: str) -> Optional[Course]:
        return db.query(Course).filter(Course.slug == slug).first()
        
    def get_published(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Course]:
        return db.query(Course).filter(Course.status == "PUBLISHED").offset(skip).limit(limit).all()

course_repo = CourseRepository(Course)
