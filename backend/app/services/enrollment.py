from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.enrollment import enrollment_repo
from app.repositories.course import course_repo
from app.models.enrollment import Enrollment
from app.models.user import User
from app.schemas.enrollment import EnrollmentDetail

class EnrollmentService:
    @staticmethod
    def enroll_user(db: Session, course_id: int, user: User) -> EnrollmentDetail:
        course = course_repo.get(db, id=course_id)
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

        existing = enrollment_repo.get_by_user_and_course(db, user_id=user.id, course_id=course_id)
        if existing:
            return EnrollmentDetail(
                id=existing.id,
                user_id=existing.user_id,
                course_id=existing.course_id,
                status=existing.status,
                enrolled_at=existing.enrolled_at,
                course_title=course.title,
                course_slug=course.slug
            )

        new_enrollment = Enrollment(
            user_id=user.id,
            course_id=course_id,
            status="ACTIVE"
        )
        db.add(new_enrollment)
        db.commit()
        db.refresh(new_enrollment)

        return EnrollmentDetail(
            id=new_enrollment.id,
            user_id=new_enrollment.user_id,
            course_id=new_enrollment.course_id,
            status=new_enrollment.status,
            enrolled_at=new_enrollment.enrolled_at,
            course_title=course.title,
            course_slug=course.slug
        )

    @staticmethod
    def get_my_courses(db: Session, user: User) -> List[EnrollmentDetail]:
        enrollments = enrollment_repo.get_user_enrollments(db, user_id=user.id)
        results = []
        for e in enrollments:
            results.append(EnrollmentDetail(
                id=e.id,
                user_id=e.user_id,
                course_id=e.course_id,
                status=e.status,
                enrolled_at=e.enrolled_at,
                course_title=e.course.title if e.course else None,
                course_slug=e.course.slug if e.course else None
            ))
        return results

enrollment_service = EnrollmentService()
