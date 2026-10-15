from datetime import datetime
from sqlalchemy.orm import Session
from app.repositories.progress import progress_repo
from app.models.progress import LectureProgress
from app.models.user import User
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
            was_completed = progress.completed
            progress.completed = update.completed
            if update.watch_time_seconds:
                progress.watch_time_seconds = update.watch_time_seconds
            if update.completed and not was_completed:
                progress.completed_at = datetime.utcnow()
                stats.total_xp += 25

        # Recalculate level: every 100 XP is 1 level
        stats.level = max(1, (stats.total_xp // 100) + 1)
        db.commit()

        return {"status": "success", "total_xp": stats.total_xp, "level": stats.level}

progress_service = ProgressService()
