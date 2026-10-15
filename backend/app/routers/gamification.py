from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.gamification import Badge, UserBadge
from app.schemas.gamification import BadgeDetail, UserStatsDetail
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.repositories.progress import progress_repo
from app.models.progress import CourseProgress

router = APIRouter(prefix="", tags=["Gamification"])

@router.get("/stats", response_model=UserStatsDetail)
@router.get("/gamification/stats", response_model=UserStatsDetail)
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve full gamification stats (XP, level, streaks, solved breakdown, badges) for the active user."""
    stats = progress_repo.get_user_stats(db, user_id=current_user.id)
    all_badges = db.query(Badge).all()
    user_badge_map = {
        ub.badge_id: ub.awarded_at
        for ub in db.query(UserBadge).filter(UserBadge.user_id == current_user.id).all()
    }

    badge_details = [
        BadgeDetail(
            id=b.id,
            slug=b.slug,
            name=b.name,
            description=b.description,
            category=b.category,
            tier=b.tier,
            icon=b.icon,
            xp_reward=b.xp_reward,
            unlocked=b.id in user_badge_map,
            unlocked_at=user_badge_map.get(b.id)
        )
        for b in all_badges
    ]

    return UserStatsDetail(
        total_xp=stats.total_xp,
        level=stats.level,
        current_streak=stats.current_streak,
        longest_streak=stats.longest_streak,
        total_solved=stats.total_solved,
        easy_solved=stats.easy_solved,
        medium_solved=stats.medium_solved,
        hard_solved=stats.hard_solved,
        badges=badge_details
    )

@router.get("/badges", response_model=List[BadgeDetail])
@router.get("/gamification/badges", response_model=List[BadgeDetail])
def get_badges(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve all badges and mark those unlocked by the user."""
    all_badges = db.query(Badge).all()
    user_badge_map = {
        ub.badge_id: ub.awarded_at
        for ub in db.query(UserBadge).filter(UserBadge.user_id == current_user.id).all()
    }

    results = []
    for b in all_badges:
        unlocked = b.id in user_badge_map
        results.append(BadgeDetail(
            id=b.id,
            slug=b.slug,
            name=b.name,
            description=b.description,
            category=b.category,
            tier=b.tier,
            icon=b.icon,
            xp_reward=b.xp_reward,
            unlocked=unlocked,
            unlocked_at=user_badge_map.get(b.id)
        ))
    return results

@router.get("/certificates")
@router.get("/gamification/certificates")
def get_certificates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve verified certificates only for completed courses (completion_percentage >= 100)."""
    completed_courses = (
        db.query(CourseProgress)
        .filter(
            CourseProgress.user_id == current_user.id,
            CourseProgress.completion_percentage >= 100.0
        )
        .all()
    )

    certs = []
    for cp in completed_courses:
        course_title = cp.course.title if cp.course else f"Course #{cp.course_id}"
        certs.append({
            "id": f"cert_{current_user.id}_{cp.course_id}",
            "title": course_title,
            "issuer": "CipherPage Academy",
            "issue_date": cp.last_accessed_at.strftime("%Y-%m-%d") if cp.last_accessed_at else "2026-08-01",
            "verification_code": f"CP-{current_user.id:04d}-{cp.course_id:04d}",
            "credential_url": f"https://verify.cipherpage.com/{current_user.id}/{cp.course_id}",
            "skills": ["Algorithms", "Full-Stack Architecture", "Software Engineering"]
        })
    return certs

