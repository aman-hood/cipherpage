from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.repositories.base import CRUDBase
from app.models.challenge import Challenge, TestCase
from app.schemas.challenge import ChallengeCreate, ChallengeBase

class ChallengeRepository(CRUDBase[Challenge, ChallengeCreate, ChallengeBase]):
    def get_by_slug(self, db: Session, *, slug: str) -> Optional[Challenge]:
        return db.query(Challenge).options(joinedload(Challenge.test_cases)).filter(Challenge.slug == slug).first()

    def get_with_test_cases(self, db: Session, *, challenge_id: int) -> Optional[Challenge]:
        return db.query(Challenge).options(joinedload(Challenge.test_cases)).filter(Challenge.id == challenge_id).first()

    def get_active_challenges(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Challenge]:
        return db.query(Challenge).filter(Challenge.is_active == True).offset(skip).limit(limit).all()

challenge_repo = ChallengeRepository(Challenge)
