from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database.session import get_db
from app.dependencies.auth import get_current_user, require_teacher
from app.models.user import User
from app.models.ai import Document
from app.models.enrollment import Enrollment
from app.schemas.ai import AIMentorRequest, AIMentorResponse, AIQuotaStatus
from app.schemas.rag import RAGQueryRequest, RAGQueryResponse, DocumentIngestRequest, DocumentDetail
from app.services.ai_mentor import ai_mentor_service
from app.services.rag_assistant import rag_service

router = APIRouter(prefix="/ai", tags=["GenAI Coding Mentor & RAG"])

@router.post("/mentor", response_model=AIMentorResponse)
def get_ai_mentor_guidance(
    req: AIMentorRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    GenAI Coding Mentor endpoint (AI-01).
    Supports 4 pedagogical modes:
    - HINT: Socratic progressive guidance (AI-02)
    - DEBUG: Error diagnosis and root cause analysis (AI-03)
    - EXPLAIN: Stepwise breakdown of logic (AI-04)
    - COMPLEXITY: Big-O time and space complexity evaluation (AI-04)
    """
    return ai_mentor_service.process_mentor_request(db, user=current_user, req=req)

@router.get("/quota", response_model=AIQuotaStatus)
def get_ai_quota(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve daily AI mentor quota status for the authenticated user (AI-07)."""
    return ai_mentor_service.get_quota_status(db, user=current_user)

@router.post("/learning-assistant", response_model=RAGQueryResponse)
def ask_learning_assistant(
    req: RAGQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    RAG Learning Assistant endpoint (RAG-01..RAG-08).
    Retrieves course materials with permission filtering and cites source sections.
    """
    return rag_service.answer_question(db, user=current_user, req=req)

@router.post("/documents/ingest", response_model=DocumentDetail, status_code=status.HTTP_201_CREATED)
def ingest_course_document(
    req: DocumentIngestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """Ingests course notes, chunks text, and computes pgvector embeddings (RAG-02)."""
    return rag_service.ingest_document(db, user=current_user, req=req)

@router.get("/documents", response_model=List[DocumentDetail])
def list_documents(
    course_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List approved documents and their ingestion status (RAG-06)."""
    query = db.query(Document).filter(Document.status == "PROCESSED")
    if current_user.role not in {"ADMIN", "TEACHER", "INSTRUCTOR"}:
        enrolled_ids = [
            row[0]
            for row in db.query(Enrollment.course_id)
            .filter(
                Enrollment.user_id == current_user.id,
                Enrollment.status.in_(["ACTIVE", "COMPLETED"]),
            )
            .all()
        ]
        if course_id is not None and course_id not in enrolled_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be enrolled in this course to access its documents",
            )
        query = query.filter(
            or_(Document.course_id.is_(None), Document.course_id.in_(enrolled_ids))
        )
    if course_id is not None:
        query = query.filter(Document.course_id == course_id)
    docs = query.order_by(Document.created_at.desc()).all()
    return [
        DocumentDetail(
            id=d.id,
            title=d.title,
            course_id=d.course_id,
            status=d.status,
            chunks_count=len(d.chunks),
            created_at=d.created_at
        )
        for d in docs
    ]

