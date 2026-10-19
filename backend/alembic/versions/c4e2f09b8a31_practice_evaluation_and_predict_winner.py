"""Add practice run modes and seed the Predict the Winner challenge.

Revision ID: c4e2f09b8a31
Revises: b7a9c51e4d20
"""

from datetime import datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c4e2f09b8a31"
down_revision: Union[str, None] = "b7a9c51e4d20"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


PREDICT_THE_WINNER_TEST_CASES = [
    ("[1, 5, 2]", "false", "Player 2 can take 5 and finish with the higher score."),
    ("[1, 5, 233, 7]", "true", "Player 1 can secure the 233."),
    ("[1, 1]", "true", "A tie is a win for Player 1."),
    ("[1, 2, 99, 4]", "true", "Player 1 can take 1 and then secure 99."),
    ("[10, 9, 1]", "true", "Player 1 can secure the larger sum of one index parity."),
    ("[1, 5, 2, 4, 6]", "true", "Player 1 can secure a tied score."),
    ("[10, 15, 20, 99, 1]", "true", "Player 1 can secure the larger parity sum."),
    ("[3, 9, 1, 2]", "false", "Player 2 can take 9 and force a higher score."),
    ("[1, 100, 1000, 50, 20, 80, 90, 12, 44, 99]", "true", "Player 1 can secure the larger parity sum."),
    ("[1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000]", "true", "Both players tie, so Player 1 wins."),
]


def upgrade() -> None:
    op.add_column(
        "submissions",
        sa.Column(
            "evaluation_mode",
            sa.String(length=16),
            nullable=False,
            server_default=sa.text("'submit'"),
        ),
    )

    challenges = sa.table(
        "challenges",
        sa.column("id", sa.Integer()),
        sa.column("title", sa.String()),
        sa.column("slug", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("difficulty", sa.String()),
        sa.column("category", sa.String()),
        sa.column("time_limit", sa.Float()),
        sa.column("memory_limit", sa.Integer()),
        sa.column("starter_code", sa.JSON()),
        sa.column("hints", sa.JSON()),
        sa.column("constraints", sa.JSON()),
        sa.column("examples", sa.JSON()),
        sa.column("is_active", sa.Boolean()),
        sa.column("created_at", sa.DateTime()),
        sa.column("updated_at", sa.DateTime()),
    )
    test_cases = sa.table(
        "test_cases",
        sa.column("id", sa.Integer()),
        sa.column("challenge_id", sa.Integer()),
        sa.column("input_data", sa.Text()),
        sa.column("expected_output", sa.Text()),
        sa.column("explanation", sa.Text()),
        sa.column("is_hidden", sa.Boolean()),
        sa.column("order", sa.Integer()),
        sa.column("created_at", sa.DateTime()),
    )

    bind = op.get_bind()
    challenge_id = bind.execute(
        sa.select(challenges.c.id).where(challenges.c.slug == "predict-the-winner")
    ).scalar_one_or_none()

    now = datetime.utcnow()
    if challenge_id is None:
        bind.execute(
            challenges.insert().values(
                title="Predict the Winner",
                slug="predict-the-winner",
                description=(
                    "Given an integer array nums, two players take turns choosing a number "
                    "from either end. Return true if Player 1 can finish with at least as "
                    "many points as Player 2 when both play optimally."
                ),
                difficulty="MEDIUM",
                category="Dynamic Programming / Game Theory",
                time_limit=2.0,
                memory_limit=256,
                starter_code={
                    "python": "class Solution:\n    def predictTheWinner(self, nums: list[int]) -> bool:\n        # Write your solution here\n        pass\n"
                },
                hints=[
                    "Track the best score difference the current player can force.",
                    "Use dynamic programming over subarrays."
                ],
                constraints=["1 <= nums.length <= 20", "0 <= nums[i] <= 10^7"],
                examples=[
                    {"input": "nums = [1, 5, 2]", "output": "false"},
                    {"input": "nums = [1, 5, 233, 7]", "output": "true"},
                ],
                is_active=True,
                created_at=now,
                updated_at=now,
            )
        )
        challenge_id = bind.execute(
            sa.select(challenges.c.id).where(challenges.c.slug == "predict-the-winner")
        ).scalar_one()
    existing_orders = set(
        bind.execute(
            sa.select(test_cases.c.order).where(test_cases.c.challenge_id == challenge_id)
        ).scalars()
    )

    for order, (input_data, expected_output, explanation) in enumerate(PREDICT_THE_WINNER_TEST_CASES, start=1):
        values = {
            "input_data": input_data,
            "expected_output": expected_output,
            "explanation": explanation,
            "is_hidden": order > 5,
        }
        if order in existing_orders:
            # Preserve existing inputs, outputs, IDs, and foreign keys. Make the five
            # visible basic cases available to Run; submissions still include all cases.
            bind.execute(
                test_cases.update()
                .where(test_cases.c.challenge_id == challenge_id)
                .where(test_cases.c.order == order)
                .values(is_hidden=values["is_hidden"])
            )
        else:
            bind.execute(
                test_cases.insert().values(
                    challenge_id=challenge_id,
                    order=order,
                    created_at=now,
                    **values,
                )
            )


def downgrade() -> None:
    # Challenge content and submissions are retained to avoid deleting user data.
    op.drop_column("submissions", "evaluation_mode")
