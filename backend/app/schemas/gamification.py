from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class BadgeBase(BaseModel):
    slug: str
    name: str
    description: str
    category: str
    tier: str
    icon: str
    xp_reward: int

class BadgeDetail(BadgeBase):
    id: int
    unlocked: bool = False
    unlocked_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserStatsDetail(BaseModel):
    total_xp: int
    level: int
    current_streak: int
    longest_streak: int
    total_solved: int
    easy_solved: int
    medium_solved: int
    hard_solved: int
    hours_learned: float = 0.0
    badges: List[BadgeDetail] = []

    class Config:
        from_attributes = True

class UserActivityDetail(BaseModel):
    id: int
    activity_type: str
    title: str
    description: Optional[str] = None
    action_label: str
    created_at: datetime

    class Config:
        from_attributes = True

class UserActivityCreate(BaseModel):
    activity_type: str
    title: str
    description: Optional[str] = None
    action_label: str

class POTDCompletionRequest(BaseModel):
    video_id: str
    problem_number: Optional[str] = None
    title: Optional[str] = None
    date_key: str
    completed: bool = True

class POTDCompletionDetail(BaseModel):
    video_id: str
    problem_number: Optional[str] = None
    date_key: str
    completed: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserDashboardSummary(BaseModel):
    stats: UserStatsDetail
    recent_activity: List[UserActivityDetail]
    solved_potds: List[str]
    hours_learned: float

