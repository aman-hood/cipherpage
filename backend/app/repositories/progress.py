from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.progress import LectureProgress, CourseProgress
from app.models.gamification import UserStats

class ProgressRepository:
    def get_user_stats(self, db: Session, *, user_id: int) -> UserStats:
        stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
        if not stats:
            stats = UserStats(
                user_id=user_id,
                total_xp=0,
                level=1,
                current_streak=0,
                longest_streak=0,
                total_solved=0,
                easy_solved=0,
                medium_solved=0,
                hard_solved=0,
                hours_learned=0.0
            )
            db.add(stats)
            db.commit()
            db.refresh(stats)
        return stats

    def get_lecture_progress(self, db: Session, *, user_id: int, lecture_id: int) -> Optional[LectureProgress]:
        return db.query(LectureProgress).filter(
            LectureProgress.user_id == user_id,
            LectureProgress.lecture_id == lecture_id
        ).first()

    def get_course_progress(self, db: Session, *, user_id: int, course_id: int) -> Optional[CourseProgress]:
        return db.query(CourseProgress).filter(
            CourseProgress.user_id == user_id,
            CourseProgress.course_id == course_id
        ).first()

progress_repo = ProgressRepository()
