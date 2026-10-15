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
    badges: List[BadgeDetail] = []

    class Config:
        from_attributes = True
