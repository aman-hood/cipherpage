from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.submission import Submission
from app.models.gamification import UserBadge, Badge

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/", response_model=List[Dict[str, Any]])
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves personalized notifications for the authenticated user,
    aggregating system announcements, submission status alerts, and unlocked badges.
    """
    notifications: List[Dict[str, Any]] = [
        {
            "id": 1,
            "title": "Welcome to CipherPage",
            "message": f"Welcome aboard, {current_user.name}! Start practicing code challenges or explore your enrolled courses.",
            "type": "SYSTEM",
            "read": True,
            "created_at": current_user.created_at.isoformat() if hasattr(current_user, "created_at") and current_user.created_at else None
        }
    ]

    # Add notifications for recently unlocked badges
    user_badges = (
        db.query(UserBadge)
        .join(Badge, UserBadge.badge_id == Badge.id)
        .filter(UserBadge.user_id == current_user.id)
        .order_by(UserBadge.awarded_at.desc())
        .limit(3)
        .all()
    )
    for ub in user_badges:
        notifications.append({
            "id": 100 + ub.id,
            "title": "Badge Unlocked!",
            "message": f"Congratulations! You unlocked the '{ub.badge.name}' badge ({ub.badge.icon}) and earned {ub.badge.xp_reward} XP.",
            "type": "ACHIEVEMENT",
            "read": False,
            "created_at": ub.awarded_at.isoformat() if ub.awarded_at else None
        })

    # Add notification for most recent code submission
    recent_sub = (
        db.query(Submission)
        .filter(Submission.user_id == current_user.id)
        .order_by(Submission.created_at.desc())
        .first()
    )
    if recent_sub:
        notifications.append({
            "id": 200 + hash(recent_sub.id) % 10000,
            "title": f"Submission {recent_sub.status.capitalize()}",
            "message": f"Your submission for Challenge #{recent_sub.challenge_id} finished with status {recent_sub.status} (Score: {recent_sub.score}%).",
            "type": "SUBMISSION",
            "read": True,
            "created_at": recent_sub.created_at.isoformat() if recent_sub.created_at else None
        })

    return notifications
