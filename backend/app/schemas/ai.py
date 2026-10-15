from typing import Optional, List
from pydantic import BaseModel, Field

class AIMentorRequest(BaseModel):
    challenge_id: Optional[int] = None
    mode: str = Field(..., description="HINT, DEBUG, EXPLAIN, or COMPLEXITY")
    code: str = Field(..., max_length=65536, description="Source code to analyze")
    language: str = Field(default="python", description="Programming language")
    error_output: Optional[str] = Field(default=None, description="Error logs for DEBUG mode")
    request_full_solution: bool = Field(default=False, description="Reveal complete solution in HINT mode")

class AIMentorResponse(BaseModel):
    mode: str
    content: str
    tokens_used: int = 0
    disclaimer: str = "AI guidance is an educational assistant and may make mistakes. Verify your logic using test cases."
    remaining_quota: int = 50

class AIQuotaStatus(BaseModel):
    daily_requests_used: int
    daily_limit: int
    remaining_quota: int
