from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    # Stable provider identity. The nullable legacy column is retained solely for
    # explicit account migration; application ownership uses the internal integer id.
    firebase_uid = Column(String, unique=True, index=True, nullable=True)
    legacy_auth_uid = Column(String, unique=True, index=True, nullable=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, default="STUDENT", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    submissions = relationship("Submission", back_populates="user", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="user", cascade="all, delete-orphan")
    lecture_progresses = relationship("LectureProgress", back_populates="user", cascade="all, delete-orphan")
    course_progresses = relationship("CourseProgress", back_populates="user", cascade="all, delete-orphan")
    badges = relationship("UserBadge", back_populates="user", cascade="all, delete-orphan")
    stats = relationship("UserStats", back_populates="user", uselist=False, cascade="all, delete-orphan")

