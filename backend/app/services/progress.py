from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.progress import progress_repo
from app.models.progress import LectureProgress
from app.models.user import User
from app.models.course import Lecture
from app.models.gamification import UserActivity
from app.dependencies.auth import ensure_course_access
from app.schemas.progress import ProgressUpdate, OverallProgress

class ProgressService:
    @staticmethod
    def get_progress(db: Session, user: User) -> OverallProgress:
        stats = progress_repo.get_user_stats(db, user_id=user.id)
        return OverallProgress(
            total_xp=stats.total_xp,
            level=stats.level,
            current_streak=stats.current_streak,
            longest_streak=stats.longest_streak,
            total_solved=stats.total_solved,
            easy_solved=stats.easy_solved,
            medium_solved=stats.medium_solved,
            hard_solved=stats.hard_solved
        )

    @staticmethod
    def update_lecture_progress(db: Session, user: User, update: ProgressUpdate) -> dict:
        lecture = db.query(Lecture).filter(Lecture.id == update.lecture_id).first()
        if lecture is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lecture not found")
        ensure_course_access(db, user, lecture.module.course)

        progress = progress_repo.get_lecture_progress(db, user_id=user.id, lecture_id=update.lecture_id)
        stats = progress_repo.get_user_stats(db, user_id=user.id)

        if not progress:
            progress = LectureProgress(
                user_id=user.id,
                lecture_id=update.lecture_id,
                completed=update.completed,
                watch_time_seconds=update.watch_time_seconds or 0,
                completed_at=datetime.utcnow() if update.completed else None
            )
            db.add(progress)
            if update.completed:
                stats.total_xp += 25
        else:
            progress.completed = update.completed
            if update.watch_time_seconds:
                progress.watch_time_seconds = update.watch_time_seconds
            if update.completed and progress.completed_at is None:
                progress.completed_at = datetime.utcnow()
                stats.total_xp += 25

        # Recalculate level: every 100 XP is 1 level
        stats.level = max(1, (stats.total_xp // 100) + 1)
        if update.completed:
            course_title = lecture.module.course.title if (lecture.module and lecture.module.course) else "Course"
            db.add(UserActivity(
                user_id=user.id,
                activity_type="LECTURE",
                title=f"Lecture: {lecture.title}",
                description=f"Completed lecture in {course_title}",
                action_label="Completed"
            ))
        db.commit()

        return {"status": "success", "total_xp": stats.total_xp, "level": stats.level}

progress_service = ProgressService()
