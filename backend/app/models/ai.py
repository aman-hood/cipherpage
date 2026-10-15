from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.base import Base

class AIUsageRecord(Base):
    __tablename__ = "ai_usage_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    mode = Column(String(50), nullable=False) # HINT, DEBUG, EXPLAIN, COMPLEXITY, RAG
    model_name = Column(String(100), nullable=False)
    prompt_tokens = Column(Integer, default=0, nullable=False)
    completion_tokens = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship("User")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="SET NULL"), nullable=True, index=True)
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    status = Column(String(50), default="PENDING", nullable=False) # PENDING, PROCESSED, FAILED
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User")
    course = relationship("Course")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

try:
    from pgvector.sqlalchemy import Vector
    EmbeddingColumnType = Vector(384)
except ImportError:
    EmbeddingColumnType = JSON

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    section_title = Column(String(255), nullable=True)
    page_number = Column(Integer, nullable=True)
    embedding = Column(EmbeddingColumnType, nullable=True) # Stored 384-dim vector representation
    token_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    document = relationship("Document", back_populates="chunks")

