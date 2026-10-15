from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class Citation(BaseModel):
    document_id: int
    document_title: str
    section_title: str
    page_number: Optional[int] = None
    excerpt: str

class RAGQueryRequest(BaseModel):
    question: str = Field(..., max_length=1000, description="Question about course materials")
    course_id: Optional[int] = Field(default=None, description="Course scope for permission-aware retrieval")

class RAGQueryResponse(BaseModel):
    question: str
    answer: str
    citations: List[Citation] = []
    sources_found: bool = True
    confidence: float = 0.95

class DocumentIngestRequest(BaseModel):
    title: str = Field(..., max_length=255)
    course_id: Optional[int] = None
    content: str = Field(..., description="Raw text or markdown content of approved course notes")

class DocumentDetail(BaseModel):
    id: int
    title: str
    course_id: Optional[int] = None
    status: str
    chunks_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True
