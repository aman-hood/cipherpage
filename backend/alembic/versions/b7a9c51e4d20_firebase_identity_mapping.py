"""Add Firebase UID support and auditable legacy identity mapping."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b7a9c51e4d20"
down_revision: Union[str, None] = "0d4b3d2be169"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Preserve old provider UIDs as migration metadata. Application ownership
    # continues to use users.id and all existing foreign keys remain untouched.
    op.drop_index("ix_users_supabase_user_id", table_name="users")
    op.alter_column(
        "users",
        "supabase_user_id",
        existing_type=sa.String(),
        nullable=True,
        new_column_name="legacy_auth_uid",
    )
    op.create_index("ix_users_legacy_auth_uid", "users", ["legacy_auth_uid"], unique=True)
    op.add_column("users", sa.Column("firebase_uid", sa.String(), nullable=True))
    op.create_index("ix_users_firebase_uid", "users", ["firebase_uid"], unique=True)

    op.create_table(
        "firebase_identity_mappings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("legacy_auth_uid", sa.String(), nullable=False),
        sa.Column("firebase_uid", sa.String(), nullable=False),
        sa.Column("verified_by", sa.String(length=255), nullable=False),
        sa.Column("verification_method", sa.String(length=64), nullable=False),
        sa.Column("evidence_ref", sa.String(length=255), nullable=False),
        sa.Column("verified_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_firebase_identity_mapping_user"),
        sa.UniqueConstraint("legacy_auth_uid", name="uq_firebase_identity_mapping_legacy_uid"),
        sa.UniqueConstraint("firebase_uid", name="uq_firebase_identity_mapping_firebase_uid"),
    )


def downgrade() -> None:
    raise RuntimeError(
        "This migration preserves Firebase identity mappings. Restore from a reviewed "
        "backup or write a data-preserving forward migration before reverting it."
    )
