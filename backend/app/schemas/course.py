from pydantic import BaseModel
from typing import List, Optional

class CourseBase(BaseModel):
    title: str
    slug: str
    description: str
    category: str
    difficulty: str

class CourseDetail(CourseBase):
    id: int
    price: float
    status: str

class ModuleBase(BaseModel):
    title: str
    order: int

class LectureBase(BaseModel):
    title: str
    duration: int
    video_url: Optional[str] = None
