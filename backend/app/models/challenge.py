from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.base import Base

class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(String, default="EASY", nullable=False) # EASY, MEDIUM, HARD
    category = Column(String, default="General", nullable=False)
    time_limit = Column(Float, default=2.0) # in seconds
    memory_limit = Column(Integer, default=256) # in MB
    starter_code = Column(JSON, nullable=True) # {"python": "...", "javascript": "...", ...}
    hints = Column(JSON, nullable=True) # list of hints
    constraints = Column(JSON, nullable=True) # list of constraint strings
    examples = Column(JSON, nullable=True) # list of example input/outputs
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    test_cases = relationship("TestCase", back_populates="challenge", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="challenge", cascade="all, delete-orphan")

class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    challenge_id = Column(Integer, ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False, index=True)
    input_data = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    is_hidden = Column(Boolean, default=True, nullable=False)
    order = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    challenge = relationship("Challenge", back_populates="test_cases")
    submission_results = relationship("SubmissionResult", back_populates="test_case", cascade="all, delete-orphan")
