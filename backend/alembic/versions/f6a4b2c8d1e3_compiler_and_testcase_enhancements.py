"""compiler and testcase enhancements

Revision ID: f6a4b2c8d1e3
Revises: e5f3a1b2c4d6
Create Date: 2026-10-21 10:45:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f6a4b2c8d1e3'
down_revision = 'e5f3a1b2c4d6'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Add custom_input to submissions
    op.add_column('submissions', sa.Column('custom_input', sa.Text(), nullable=True))
    
    # 2. Make test_case_id nullable in submission_results to accommodate custom test evaluations
    op.alter_column('submission_results', 'test_case_id', existing_type=sa.Integer(), nullable=True)

def downgrade() -> None:
    op.alter_column('submission_results', 'test_case_id', existing_type=sa.Integer(), nullable=False)
    op.drop_column('submissions', 'custom_input')
