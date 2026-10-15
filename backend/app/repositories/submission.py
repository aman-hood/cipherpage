from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.repositories.base import CRUDBase
from app.models.submission import Submission, SubmissionResult
from app.schemas.submission import CodeSubmission

class SubmissionRepository(CRUDBase[Submission, CodeSubmission, CodeSubmission]):
    def get_by_submission_id(self, db: Session, *, submission_id: str) -> Optional[Submission]:
        return (
            db.query(Submission)
            .options(joinedload(Submission.results))
            .filter(Submission.id == submission_id)
            .first()
        )

    def get_user_submissions(
        self, db: Session, *, user_id: int, challenge_id: Optional[int] = None, skip: int = 0, limit: int = 20
    ) -> List[Submission]:
        query = db.query(Submission).filter(Submission.user_id == user_id)
        if challenge_id:
            query = query.filter(Submission.challenge_id == challenge_id)
        return query.order_by(Submission.created_at.desc()).offset(skip).limit(limit).all()

submission_repo = SubmissionRepository(Submission)
