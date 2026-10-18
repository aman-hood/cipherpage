from app.models.user import User
from app.models.course import Course, Module, Lecture
from app.models.challenge import Challenge, TestCase
from app.models.submission import Submission, SubmissionResult
from app.models.enrollment import Enrollment
from app.models.progress import LectureProgress, CourseProgress
from app.models.gamification import Badge, UserBadge, UserStats
from app.models.ai import AIUsageRecord, Document, DocumentChunk
from app.models.identity_mapping import FirebaseIdentityMapping

__all__ = [
    "User",
    "Course",
    "Module",
    "Lecture",
    "Challenge",
    "TestCase",
    "Submission",
    "SubmissionResult",
    "Enrollment",
    "LectureProgress",
    "CourseProgress",
    "Badge",
    "UserBadge",
    "UserStats",
    "AIUsageRecord",
    "Document",
    "DocumentChunk",
    "FirebaseIdentityMapping",
]
