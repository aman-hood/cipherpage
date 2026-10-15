from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class ProgressUpdate(BaseModel):
    lecture_id: int
    completed: bool
    watch_time_seconds: Optional[int] = 0

class LectureProgressDetail(BaseModel):
    id: int
    lecture_id: int
    completed: bool
    watch_time_seconds: int
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class OverallProgress(BaseModel):
    total_xp: int = 0
    level: int = 1
    current_streak: int = 0
    longest_streak: int = 0
    total_solved: int = 0
    easy_solved: int = 0
    medium_solved: int = 0
    hard_solved: int = 0

    class Config:
        from_attributes = True
