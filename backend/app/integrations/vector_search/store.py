"""
Vector Search Store for CipherPage RAG (RAG-03, RAG-08).
Enforces course enrollment / role-based filtering before retrieved content reaches the model.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from app.models.ai import Document, DocumentChunk
from app.integrations.vector_search.embeddings import embedding_generator

class VectorSearchStore:
    @staticmethod
    def search_similar_chunks(
        db: Session,
        query: str,
        course_id: Optional[int] = None,
        allowed_course_ids: Optional[List[int]] = None,
        top_k: int = 4,
        min_similarity: float = 0.25
    ) -> List[Dict[str, Any]]:
        """
        Embeds query and searches for relevant document chunks
        filtered by authorized course IDs (RAG-03).
        """
        query_vector = embedding_generator.embed_text(query)

        # Base query joining document to verify status and course
        query_db = (
            db.query(DocumentChunk)
            .join(Document, DocumentChunk.document_id == Document.id)
            .filter(Document.status == "PROCESSED")
            .options(joinedload(DocumentChunk.document))
        )

        # Apply permission filter (RAG-03)
        if course_id:
            query_db = query_db.filter(Document.course_id == course_id)
        elif allowed_course_ids is not None:
            # Allow public documents (course_id is None) or enrolled courses
            query_db = query_db.filter(
                (Document.course_id.is_(None)) | (Document.course_id.in_(allowed_course_ids))
            )

        # Check if native pgvector cosine_distance operator is available
        has_native_vector = hasattr(DocumentChunk.embedding, "cosine_distance")
        chunks = []
        if has_native_vector:
            try:
                chunks = (
                    query_db
                    .filter(DocumentChunk.embedding.isnot(None))
                    .order_by(DocumentChunk.embedding.cosine_distance(query_vector))
                    .limit(top_k * 3)
                    .all()
                )
            except Exception:
                chunks = query_db.all()
        else:
            chunks = query_db.all()

        import re
        query_words = set(re.findall(r'[a-zA-Z0-9_]{3,}', query.lower())) - {
            'the', 'is', 'a', 'an', 'and', 'of', 'in', 'to', 'for', 'with', 'on', 'at', 
            'from', 'by', 'this', 'that', 'it', 'as', 'are', 'was', 'be', 'how', 'what', 
            'why', 'can', 'does', 'which'
        }

        scored_chunks = []

        for chunk in chunks:
            if not chunk.embedding:
                continue

            # Hybrid check: require lexical overlap or strong dense alignment (RAG-05)
            chunk_words = set(re.findall(r'[a-zA-Z0-9_]{3,}', chunk.content.lower()))
            has_term_overlap = bool(query_words & chunk_words)

            sim = embedding_generator.cosine_similarity(query_vector, chunk.embedding)
            if not has_term_overlap and sim < 0.55:
                continue

            if sim >= min_similarity:
                scored_chunks.append({
                    "chunk_id": chunk.id,
                    "document_id": chunk.document.id,
                    "document_title": chunk.document.title,
                    "section_title": chunk.section_title or "General",
                    "page_number": chunk.page_number,
                    "content": chunk.content,
                    "similarity": round(sim, 4)
                })

        # Sort descending by similarity
        scored_chunks.sort(key=lambda x: x["similarity"], reverse=True)
        return scored_chunks[:top_k]

vector_store = VectorSearchStore()
