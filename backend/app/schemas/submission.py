from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class CodeSubmission(BaseModel):
    challenge_id: int
    code: str = Field(..., max_length=65536, description="Source code")
    language: str = Field(..., description="python, javascript, typescript, cpp, java, go")

class SubmissionResultDetail(BaseModel):
    id: int
    test_case_id: int
    passed: bool
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    execution_time: float
    memory_usage: float

    class Config:
        from_attributes = True

class EvaluationResult(BaseModel):
    submission_id: str
    challenge_id: int
    status: str # QUEUED, RUNNING, PASSED, FAILED, COMPILE_ERROR, RUNTIME_ERROR, TIME_LIMIT_EXCEEDED, SYSTEM_ERROR
    score: float
    tests_passed: int
    total_tests: int
    execution_time: float
    memory_usage: float
    error_message: Optional[str] = None
    created_at: datetime
    results: Optional[List[SubmissionResultDetail]] = None

    class Config:
        from_attributes = True

class SubmissionStatusResponse(BaseModel):
    submission_id: str
    status: str
    tests_passed: int = 0
    total_tests: int = 0
    score: float = 0.0
