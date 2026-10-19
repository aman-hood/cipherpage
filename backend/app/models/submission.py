from datetime import datetime
import uuid
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

def generate_submission_id():
    return f"sub_{uuid.uuid4().hex[:12]}"

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(String(32), primary_key=True, default=generate_submission_id, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    challenge_id = Column(Integer, ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(Text, nullable=False)
    language = Column(String(50), nullable=False)
    evaluation_mode = Column(String(16), default="submit", nullable=False, server_default="submit")
    status = Column(String(50), default="QUEUED", nullable=False, index=True) 
    # Statuses: QUEUED, RUNNING, PASSED, FAILED, COMPILE_ERROR, RUNTIME_ERROR, TIME_LIMIT_EXCEEDED, SYSTEM_ERROR
    score = Column(Float, default=0.0)
    tests_passed = Column(Integer, default=0)
    total_tests = Column(Integer, default=0)
    execution_time = Column(Float, default=0.0) # in seconds
    memory_usage = Column(Float, default=0.0) # in MB
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship("User", back_populates="submissions")
    challenge = relationship("Challenge", back_populates="submissions")
    results = relationship("SubmissionResult", back_populates="submission", cascade="all, delete-orphan")

class SubmissionResult(Base):
    __tablename__ = "submission_results"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(String(32), ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False, index=True)
    test_case_id = Column(Integer, ForeignKey("test_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    passed = Column(Boolean, nullable=False)
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    execution_time = Column(Float, default=0.0)
    memory_usage = Column(Float, default=0.0)

    submission = relationship("Submission", back_populates="results")
    test_case = relationship("TestCase", back_populates="submission_results")
