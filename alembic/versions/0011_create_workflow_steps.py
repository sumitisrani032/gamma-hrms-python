"""create workflow steps table (Rails: 20260413070002_create_workflow_steps)

Revision ID: 0011
Revises: 0010
Create Date: 2026-05-25
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workflow_steps",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("workflow_definition_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("step_order", sa.Integer(), nullable=False),
        sa.Column("approver_type", sa.String(length=50), nullable=False),
        sa.Column("approver_value", sa.String(length=255), nullable=True),
        sa.Column("action_on_reject", sa.String(length=20), nullable=False, server_default=sa.text("'terminate'")),
        sa.Column("auto_escalation_hours", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index("ix_workflow_steps_workflow_definition_id", "workflow_steps", ["workflow_definition_id"], unique=False)
    op.create_index("idx_workflow_steps_def_order", "workflow_steps", ["workflow_definition_id", "step_order"], unique=True)

    op.create_foreign_key(
        "fk_wf_steps_wf_def_id_wf_defs",
        "workflow_steps",
        "workflow_definitions",
        ["workflow_definition_id"],
        ["id"],
        ondelete=None,
    )


def downgrade() -> None:
    op.drop_constraint("fk_wf_steps_wf_def_id_wf_defs", "workflow_steps", type_="foreignkey")
    op.drop_index("idx_workflow_steps_def_order", table_name="workflow_steps")
    op.drop_index("ix_workflow_steps_workflow_definition_id", table_name="workflow_steps")
    op.drop_table("workflow_steps")
