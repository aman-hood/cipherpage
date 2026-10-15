from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.repositories.base import CRUDBase
from app.models.enrollment import Enrollment
from app.schemas.enrollment import EnrollmentCreate

class EnrollmentRepository(CRUDBase[Enrollment, EnrollmentCreate, EnrollmentCreate]):
    def get_by_user_and_course(self, db: Session, *, user_id: int, course_id: int) -> Optional[Enrollment]:
        return db.query(Enrollment).filter(
            Enrollment.user_id == user_id,
            Enrollment.course_id == course_id
        ).first()

    def get_user_enrollments(self, db: Session, *, user_id: int) -> List[Enrollment]:
        return (
            db.query(Enrollment)
            .options(joinedload(Enrollment.course))
            .filter(Enrollment.user_id == user_id)
            .all()
        )

enrollment_repo = EnrollmentRepository(Enrollment)
