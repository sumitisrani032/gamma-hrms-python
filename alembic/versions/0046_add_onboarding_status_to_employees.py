"""add onboarding status to employees (Rails: 20260414090001_add_onboarding_status_to_employees)

Revision ID: 0046
Revises: 0045
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa

revision = "0046"
down_revision = "0045"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("employees", sa.Column("onboarding_status", sa.String(length=20), nullable=True, server_default=sa.text("'invited'")))
    op.create_index("ix_employees_onboarding_status", "employees", ["onboarding_status"])


def downgrade() -> None:
    op.drop_index("ix_employees_onboarding_status", table_name="employees")
    op.drop_column("employees", "onboarding_status")
