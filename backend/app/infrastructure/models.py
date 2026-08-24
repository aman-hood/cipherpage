import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text, Float, JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class UserRole(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class TrackCategory(str, enum.Enum):
    LEARN = "learn"
    APPLY = "apply"
    GROW = "grow"

class User(Base):
    """User accounts including Students, Teachers, and Admins."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT, nullable=False)
    full_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    progress = relationship("StudentProgress", back_populates="student", uselist=False)
    submissions = relationship("Submission", back_populates="student")


class Course(Base):
    """High-level courses or tracks (e.g., Python Backend, Flutter Mobile)."""
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    language = Column(String)   # e.g., Python, Dart
    framework = Column(String)  # e.g., FastAPI, Flutter
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan")


class Module(Base):
    """A specific phase in the course, categorizing the 'LAG' loop."""
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String, nullable=False)
    category = Column(Enum(TrackCategory), nullable=False)
    order = Column(Integer, default=0)

    # Relationships
    course = relationship("Course", back_populates="modules")
    learning_contents = relationship("LearningContent", back_populates="module", cascade="all, delete-orphan")
    challenges = relationship("Challenge", back_populates="module", cascade="all, delete-orphan")
    portfolio_projects = relationship("PortfolioProject", back_populates="module", cascade="all, delete-orphan")


class LearningContent(Base):
    """The 'Learn' section containing video lectures, notes, and references."""
    __tablename__ = "learning_contents"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False)
    title = Column(String, nullable=False)
    video_hls_url = Column(String)  # HLS/M3U8 stream URL
    notes = Column(Text)            # Markdown or rich text notes
    starter_code_url = Column(String) # Link to lecture coding files/repo
    order = Column(Integer, default=0)

    # Relationships
    module = relationship("Module", back_populates="learning_contents")


class Challenge(Base):
    """The 'Apply' section featuring coding problems and test cases."""
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    boilerplate_code = Column(Text)
    expected_input_output = Column(JSON)  # Expected mock I/O
    test_cases_url = Column(String)       # URL to hidden unit test files used by grading worker
    difficulty = Column(String)           # Easy, Medium, Hard

    # Relationships
    module = relationship("Module", back_populates="challenges")
    submissions = relationship("Submission", back_populates="challenge")


class Submission(Base):
    """Student code submissions for Challenges in the 'Apply' section."""
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False)
    submitted_code = Column(Text, nullable=False)
    score = Column(Float, default=0.0)
    passed_tests = Column(Integer, default=0)
    total_tests = Column(Integer, default=0)
    status = Column(String, default="pending")  # pending, graded, failed
    submitted_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("User", back_populates="submissions")
    challenge = relationship("Challenge", back_populates="submissions")


class PortfolioProject(Base):
    """The 'Grow' section projects unlocked after accumulating enough score."""
    __tablename__ = "portfolio_projects"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    requirements = Column(Text)
    unlock_threshold_score = Column(Float, default=80.0) # Score required from 'Apply' section to unlock

    # Relationships
    module = relationship("Module", back_populates="portfolio_projects")


class StudentProgress(Base):
    """Tracking overall student progress across the LAG lifecycle."""
    __tablename__ = "student_progress"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    completed_content_ids = Column(JSON, default=list)    # IDs of completed LearningContents
    completed_challenge_ids = Column(JSON, default=list)  # IDs of completed Challenges
    unlocked_project_ids = Column(JSON, default=list)     # IDs of unlocked PortfolioProjects
    last_active = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("User", back_populates="progress")
