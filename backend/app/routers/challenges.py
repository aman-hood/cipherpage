from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.services.challenge import challenge_service
from app.schemas.challenge import ChallengeDetail, ChallengeCreate
from app.dependencies.auth import require_teacher
from app.models.user import User

router = APIRouter(prefix="/challenges", tags=["Challenges"])

@router.get("/", response_model=List[ChallengeDetail])
def list_challenges(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all active challenges with sanitized test cases."""
    challenges = challenge_service.get_challenges(db, skip=skip, limit=limit)
    return [challenge_service.get_challenge_by_id(db, challenge_id=c.id) for c in challenges]

@router.get("/{challenge_id}", response_model=ChallengeDetail)
def get_challenge(challenge_id: int, db: Session = Depends(get_db)):
    """Retrieve detailed challenge data without leaking hidden test case expected outputs."""
    return challenge_service.get_challenge_by_id(db, challenge_id=challenge_id)

@router.post("/", response_model=ChallengeDetail, status_code=status.HTTP_201_CREATED)
def create_challenge(
    challenge_in: ChallengeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """Create a new challenge (Teacher / Admin role required)."""
    challenge = challenge_service.create_challenge(db, challenge_in=challenge_in)
    return challenge_service.get_challenge_by_id(db, challenge_id=challenge.id, sanitize_hidden=False)
