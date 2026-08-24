from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# ================= Auth Schemas =================
class Token(BaseModel):
    access_token: str
    token_type: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str
    full_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    user: UserResponse
    token: Token


# ================= Course & LAG Schemas =================
class CourseResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    language: Optional[str] = None
    framework: Optional[str] = None

class PaginatedCourses(BaseModel):
    total: int
    page: int
    size: int
    items: List[CourseResponse]

class LectureMetadataResponse(BaseModel):
    id: int
    title: str
    video_hls_url: str
    notes: str
    starter_code_url: str


# ================= Apply (Submission) Schemas =================
class CodeSubmission(BaseModel):
    challenge_id: int
    submitted_code: str

class CodeSubmissionResponse(BaseModel):
    submission_id: int
    message: str
