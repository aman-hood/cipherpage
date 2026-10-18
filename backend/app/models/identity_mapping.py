from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint

from app.database.base import Base


class FirebaseIdentityMapping(Base):
    """Audit record for a manually verified legacy-to-Firebase identity mapping."""

    __tablename__ = "firebase_identity_mappings"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_firebase_identity_mapping_user"),
        UniqueConstraint("legacy_auth_uid", name="uq_firebase_identity_mapping_legacy_uid"),
        UniqueConstraint("firebase_uid", name="uq_firebase_identity_mapping_firebase_uid"),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    legacy_auth_uid = Column(String, nullable=False)
    firebase_uid = Column(String, nullable=False)
    verified_by = Column(String(255), nullable=False)
    verification_method = Column(String(64), nullable=False)
    evidence_ref = Column(String(255), nullable=False)
    verified_at = Column(DateTime, default=datetime.utcnow, nullable=False)
