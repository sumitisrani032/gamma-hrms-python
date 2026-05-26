"""allow null assigned_to on workflow step instances (Rails: 20260420120001_allow_null_assigned_to_on_workflow_step_instances)

Revision ID: 0057
Revises: 0056
Create Date: 2026-05-26
"""

from alembic import op

revision = "0057"
down_revision = "0056"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("workflow_step_instances", "assigned_to_id", nullable=True)


def downgrade() -> None:
    op.alter_column("workflow_step_instances", "assigned_to_id", nullable=False)
