from pydantic import BaseModel, Field
from typing import Optional

class CodeSubmissionSchema(BaseModel):
    challenge_id: int = Field(..., description="The ID of the programming challenge being attempted.")
    language: str = Field(..., description="Programming language, e.g., 'python', 'javascript'")
    source_code: str = Field(..., min_length=1, description="Raw source code string submitted by the student.")

class SubmissionStatusResponse(BaseModel):
    submission_id: int
    status: str = Field(..., description="'pending', 'passed', 'failed', or 'error'")
    score: float = Field(..., description="Scorecard percentage from 0 to 100")
    passed_tests: int
    total_tests: int
    error_logs: Optional[str] = Field(None, description="Detailed tracebacks or failed output logs.")
