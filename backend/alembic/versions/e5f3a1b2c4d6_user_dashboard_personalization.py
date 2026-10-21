"""User dashboard personalization, activities, and POTD completion tracking.

Revision ID: e5f3a1b2c4d6
Revises: c4e2f09b8a31
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

revision: str = "e5f3a1b2c4d6"
down_revision: Union[str, None] = "c4e2f09b8a31"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add hours_learned to user_stats if not present
    op.add_column(
        "user_stats",
        sa.Column("hours_learned", sa.Float(), nullable=False, server_default=sa.text("0.0")),
    )

    # 2. Create user_potd_completions table for personalized daily problem tracking
    op.create_table(
        "user_potd_completions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("video_id", sa.String(length=50), nullable=False),
        sa.Column("problem_number", sa.String(length=50), nullable=True),
        sa.Column("date_key", sa.String(length=20), nullable=False),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "video_id", name="uq_user_potd_completion"),
    )
    op.create_index("ix_user_potd_completions_user_id", "user_potd_completions", ["user_id"])
    op.create_index("ix_user_potd_completions_video_id", "user_potd_completions", ["video_id"])
    op.create_index("ix_user_potd_completions_date_key", "user_potd_completions", ["date_key"])

    # 3. Create user_activities table for personalized audit and recent activity feed
    op.create_table(
        "user_activities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("activity_type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("action_label", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_activities_user_id", "user_activities", ["user_id"])
    op.create_index("ix_user_activities_created_at", "user_activities", ["created_at"])

    # 4. Safe data repair: reset zero-activity accounts that previously received a default 1-day streak
    conn = op.get_bind()
    conn.execute(
        text("UPDATE user_stats SET current_streak = 0, longest_streak = 0 WHERE total_solved = 0 AND current_streak = 1")
    )


def downgrade() -> None:
    op.drop_index("ix_user_activities_created_at", table_name="user_activities")
    op.drop_index("ix_user_activities_user_id", table_name="user_activities")
    op.drop_table("user_activities")

    op.drop_index("ix_user_potd_completions_date_key", table_name="user_potd_completions")
    op.drop_index("ix_user_potd_completions_video_id", table_name="user_potd_completions")
    op.drop_index("ix_user_potd_completions_user_id", table_name="user_potd_completions")
    op.drop_table("user_potd_completions")

    op.drop_column("user_stats", "hours_learned")
