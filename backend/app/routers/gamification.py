from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.gamification import Badge, UserBadge, UserStats, UserActivity, UserPOTDCompletion
from app.schemas.gamification import (
    BadgeDetail,
    UserStatsDetail,
    UserActivityDetail,
    UserActivityCreate,
    POTDCompletionRequest,
    POTDCompletionDetail,
    UserDashboardSummary
)
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.repositories.progress import progress_repo
from app.models.progress import CourseProgress

router = APIRouter(prefix="", tags=["Gamification"])


def _calculate_streak_for_user(db: Session, user_id: int) -> int:
    completions = (
        db.query(UserPOTDCompletion.date_key)
        .filter(UserPOTDCompletion.user_id == user_id, UserPOTDCompletion.completed.is_(True))
        .all()
    )
    dates = {c[0] for c in completions if c[0]}
    if not dates:
        return 0

    streak = 0
    today = datetime.utcnow().date()
    check_date = today
    if check_date.isoformat() not in dates:
        check_date = today - timedelta(days=1)
        if check_date.isoformat() not in dates:
            return 0

    while check_date.isoformat() in dates:
        streak += 1
        check_date = check_date - timedelta(days=1)
    return streak


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
        hours_learned=stats.hours_learned or 0.0,
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


@router.get("/activity", response_model=List[UserActivityDetail])
@router.get("/gamification/activity", response_model=List[UserActivityDetail])
def get_user_activities(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve recent learning activities specifically for the authenticated user."""
    activities = (
        db.query(UserActivity)
        .filter(UserActivity.user_id == current_user.id)
        .order_by(UserActivity.created_at.desc())
        .limit(limit)
        .all()
    )
    return activities


@router.post("/activity", response_model=UserActivityDetail, status_code=status.HTTP_201_CREATED)
@router.post("/gamification/activity", response_model=UserActivityDetail, status_code=status.HTTP_201_CREATED)
def record_user_activity(
    activity_in: UserActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record an audit activity (e.g. video watched, problem attempted) for the authenticated user."""
    activity = UserActivity(
        user_id=current_user.id,
        activity_type=activity_in.activity_type,
        title=activity_in.title,
        description=activity_in.description,
        action_label=activity_in.action_label
    )
    db.add(activity)

    stats = progress_repo.get_user_stats(db, user_id=current_user.id)
    if activity_in.action_label.lower() in ["watched", "learned"] or activity_in.activity_type == "VIDEO_WATCHED":
        stats.hours_learned = round(stats.hours_learned + 0.5, 1)

    db.commit()
    db.refresh(activity)
    return activity


@router.get("/potd", response_model=List[POTDCompletionDetail])
@router.get("/gamification/potd", response_model=List[POTDCompletionDetail])
def get_user_potds(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve all POTD problem completions for the authenticated user."""
    completions = (
        db.query(UserPOTDCompletion)
        .filter(UserPOTDCompletion.user_id == current_user.id, UserPOTDCompletion.completed.is_(True))
        .all()
    )
    return completions


@router.post("/potd", response_model=UserDashboardSummary)
@router.post("/gamification/potd", response_model=UserDashboardSummary)
def toggle_potd_completion(
    req: POTDCompletionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Toggle a POTD problem as completed or uncompleted for the authenticated user and update their streak/XP."""
    existing = (
        db.query(UserPOTDCompletion)
        .filter(
            UserPOTDCompletion.user_id == current_user.id,
            UserPOTDCompletion.video_id == req.video_id
        )
        .first()
    )

    stats = progress_repo.get_user_stats(db, user_id=current_user.id)
    was_completed = existing.completed if existing else False
    is_now_completed = req.completed

    if not existing:
        existing = UserPOTDCompletion(
            user_id=current_user.id,
            video_id=req.video_id,
            problem_number=req.problem_number,
            date_key=req.date_key,
            completed=is_now_completed
        )
        db.add(existing)
    else:
        existing.completed = is_now_completed
        existing.date_key = req.date_key
        if req.problem_number:
            existing.problem_number = req.problem_number

    if is_now_completed and not was_completed:
        stats.total_solved += 1
        stats.total_xp += 50
        stats.hours_learned = round(stats.hours_learned + 0.5, 1)
        stats.level = max(1, (stats.total_xp // 100) + 1)
        db.flush()

        new_streak = _calculate_streak_for_user(db, current_user.id)
        stats.current_streak = new_streak
        stats.longest_streak = max(stats.longest_streak, new_streak)

        title_text = req.title or (f"Problem #{req.problem_number}" if req.problem_number else "Daily POTD")
        activity = UserActivity(
            user_id=current_user.id,
            activity_type="POTD",
            title=title_text,
            description=f"Solved daily POTD challenge for {req.date_key}",
            action_label="Solved"
        )
        db.add(activity)

    elif not is_now_completed and was_completed:
        stats.total_solved = max(0, stats.total_solved - 1)
        stats.total_xp = max(0, stats.total_xp - 50)
        stats.level = max(1, (stats.total_xp // 100) + 1)
        db.flush()

        new_streak = _calculate_streak_for_user(db, current_user.id)
        stats.current_streak = new_streak

    db.commit()

    return get_user_dashboard(db=db, current_user=current_user)


@router.get("/dashboard", response_model=UserDashboardSummary)
@router.get("/gamification/dashboard", response_model=UserDashboardSummary)
def get_user_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Consolidated endpoint returning fully personalized stats, recent activity, and solved POTDs for the active user."""
    stats_detail = get_user_stats(db=db, current_user=current_user)
    recent_activity = (
        db.query(UserActivity)
        .filter(UserActivity.user_id == current_user.id)
        .order_by(UserActivity.created_at.desc())
        .limit(10)
        .all()
    )
    solved_potds = [
        c.video_id
        for c in db.query(UserPOTDCompletion.video_id)
        .filter(UserPOTDCompletion.user_id == current_user.id, UserPOTDCompletion.completed.is_(True))
        .all()
    ]

    return UserDashboardSummary(
        stats=stats_detail,
        recent_activity=recent_activity,
        solved_potds=solved_potds,
        hours_learned=stats_detail.hours_learned
    )


