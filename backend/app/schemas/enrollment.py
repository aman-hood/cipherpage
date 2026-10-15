from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class EnrollmentCreate(BaseModel):
    course_id: int

class EnrollmentDetail(BaseModel):
    id: int
    user_id: int
    course_id: int
    status: str
    enrolled_at: datetime
    course_title: Optional[str] = None
    course_slug: Optional[str] = None
    completion_percentage: Optional[float] = 0.0

    class Config:
        from_attributes = True
