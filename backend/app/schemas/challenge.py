from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field

class TestCaseBase(BaseModel):
    input_data: str
    expected_output: str
    explanation: Optional[str] = None
    is_hidden: bool = True
    order: int = 1

class TestCaseCreate(TestCaseBase):
    pass

class TestCaseDetail(BaseModel):
    id: int
    input_data: str
    expected_output: Optional[str] = None # Omitted or redacted for hidden tests
    explanation: Optional[str] = None
    is_hidden: bool
    order: int

    class Config:
        from_attributes = True

class ChallengeBase(BaseModel):
    title: str
    slug: str
    description: str
    difficulty: str = Field(..., description="EASY, MEDIUM, or HARD")
    category: str = "General"
    time_limit: float = 2.0
    memory_limit: int = 256

class ChallengeCreate(ChallengeBase):
    starter_code: Optional[Dict[str, str]] = None
    hints: Optional[List[str]] = None
    constraints: Optional[List[str]] = None
    examples: Optional[List[Dict[str, Any]]] = None
    test_cases: Optional[List[TestCaseCreate]] = None

class ChallengeList(ChallengeBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class ChallengeDetail(ChallengeBase):
    id: int
    starter_code: Optional[Dict[str, str]] = None
    hints: Optional[List[str]] = None
    constraints: Optional[List[str]] = None
    examples: Optional[List[Dict[str, Any]]] = None
    is_active: bool
    created_at: datetime
    test_cases: Optional[List[TestCaseDetail]] = None

    class Config:
        from_attributes = True
