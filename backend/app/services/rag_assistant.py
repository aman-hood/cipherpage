"""
RAG Learning Assistant Service for CipherPage (RAG-01..RAG-08).
Enforces permission-aware context filtering (RAG-03), cites sources (RAG-04),
and refrains from hallucinating when evidence is insufficient (RAG-05).
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.models.ai import Document, DocumentChunk, AIUsageRecord
from app.models.enrollment import Enrollment
from app.schemas.rag import RAGQueryRequest, RAGQueryResponse, Citation, DocumentIngestRequest, DocumentDetail
from app.integrations.vector_search.chunker import chunker
from app.integrations.vector_search.embeddings import embedding_generator
from app.integrations.vector_search.store import vector_store
from app.integrations.llm.adapter import llm_adapter

class RAGAssistantService:
    @staticmethod
    def ingest_document(db: Session, user: User, req: DocumentIngestRequest) -> DocumentDetail:
        # Create Document record
        doc = Document(
            title=req.title,
            course_id=req.course_id,
            uploaded_by=user.id,
            file_path="in-memory-notes",
            status="PROCESSING"
        )
        db.add(doc)
        db.flush()

        try:
            # 1. Chunk document text (RAG-02, RAG-07)
            chunks_data = chunker.chunk_text(req.content, default_section=req.title)

            # 2. Embed and store chunks
            for c in chunks_data:
                vec = embedding_generator.embed_text(c["content"])
                chunk_obj = DocumentChunk(
                    document_id=doc.id,
                    chunk_index=c["chunk_index"],
                    content=c["content"],
                    section_title=c.get("section_title"),
                    page_number=1,
                    embedding=vec,
                    token_count=c.get("token_count", 0)
                )
                db.add(chunk_obj)

            doc.status = "PROCESSED"
            db.commit()
            db.refresh(doc)

            return DocumentDetail(
                id=doc.id,
                title=doc.title,
                course_id=doc.course_id,
                status=doc.status,
                chunks_count=len(chunks_data),
                created_at=doc.created_at
            )
        except Exception as e:
            db.rollback()
            try:
                failed_doc = Document(
                    title=req.title,
                    course_id=req.course_id,
                    uploaded_by=user.id,
                    file_path="in-memory-notes",
                    status="FAILED"
                )
                db.add(failed_doc)
                db.commit()
            except Exception:
                db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Document ingestion failed",
            ) from e

    @staticmethod
    def answer_question(db: Session, user: User, req: RAGQueryRequest) -> RAGQueryResponse:
        # 1. Permission-aware scope checking (RAG-03)
        enrolled_ids: Optional[List[int]] = None
        if user.role not in ["ADMIN", "TEACHER", "INSTRUCTOR"]:
            enrolled = db.query(Enrollment.course_id).filter(
                Enrollment.user_id == user.id,
                Enrollment.status.in_(["ACTIVE", "COMPLETED"]),
            ).all()
            enrolled_ids = [e[0] for e in enrolled]
            if req.course_id and req.course_id not in enrolled_ids:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You must be enrolled in this course to access its learning resources."
                )

        # 2. Retrieve relevant chunks (RAG-08)
        matched_chunks = vector_store.search_similar_chunks(
            db=db,
            query=req.question,
            course_id=req.course_id,
            allowed_course_ids=enrolled_ids,
            top_k=3,
            min_similarity=0.20
        )

        # 3. Grounded response or refusal when unsupported (RAG-05)
        if not matched_chunks:
            return RAGQueryResponse(
                question=req.question,
                answer=(
                    "The approved course notes and documentation do not contain sufficient information to answer this question. "
                    "Please consult your course syllabus or ask your instructor in the discussion forum."
                ),
                citations=[],
                sources_found=False,
                confidence=0.0
            )

        # 4. Synthesize answer with citations (RAG-04)
        citations: List[Citation] = []
        context_snippets = []

        for c in matched_chunks:
            citations.append(Citation(
                document_id=c["document_id"],
                document_title=c["document_title"],
                section_title=c["section_title"],
                page_number=c.get("page_number"),
                excerpt=c["content"][:200] + ("..." if len(c["content"]) > 200 else "")
            ))
            context_snippets.append(f"[{c['document_title']} - {c['section_title']}]: {c['content']}")

        # Formulate grounded educational answer synthesized via LLM
        primary_snippet = matched_chunks[0]
        grounded_answer, model_used, tokens = llm_adapter.synthesize_rag_response(
            question=req.question,
            context_snippets=context_snippets
        )

        # Log AI usage
        usage = AIUsageRecord(
            user_id=user.id,
            mode="RAG",
            model_name=model_used,
            prompt_tokens=tokens,
            completion_tokens=int(tokens * 0.75)
        )
        db.add(usage)
        db.commit()

        return RAGQueryResponse(
            question=req.question,
            answer=grounded_answer,
            citations=citations,
            sources_found=True,
            confidence=round(primary_snippet["similarity"], 2)
        )

rag_service = RAGAssistantService()
