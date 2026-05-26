"""create workflow step instances table (Rails: 20260413070004_create_workflow_step_instances)

Revision ID: 0013
Revises: 0012
Create Date: 2026-05-25
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0013"
down_revision = "0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workflow_step_instances",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("workflow_instance_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workflow_step_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assigned_to_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("comments", sa.Text(), nullable=True),
        sa.Column("acted_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index("ix_workflow_step_instances_workflow_instance_id", "workflow_step_instances", ["workflow_instance_id"], unique=False)
    op.create_index("ix_workflow_step_instances_workflow_step_id", "workflow_step_instances", ["workflow_step_id"], unique=False)
    op.create_index("ix_workflow_step_instances_assigned_to_id", "workflow_step_instances", ["assigned_to_id"], unique=False)
    op.create_index("ix_workflow_step_instances_status", "workflow_step_instances", ["status"], unique=False)

    op.create_foreign_key(
        "fk_wf_step_inst_wf_inst_id_wf_insts",
        "workflow_step_instances",
        "workflow_instances",
        ["workflow_instance_id"],
        ["id"],
        ondelete=None,
    )
    op.create_foreign_key(
        "fk_wf_step_inst_wf_step_id_wf_steps",
        "workflow_step_instances",
        "workflow_steps",
        ["workflow_step_id"],
        ["id"],
        ondelete=None,
    )
    op.create_foreign_key(
        "fk_wf_step_inst_assigned_to_id_users",
        "workflow_step_instances",
        "users",
        ["assigned_to_id"],
        ["id"],
        ondelete=None,
    )


def downgrade() -> None:
    op.drop_constraint("fk_wf_step_inst_assigned_to_id_users", "workflow_step_instances", type_="foreignkey")
    op.drop_constraint("fk_wf_step_inst_wf_step_id_wf_steps", "workflow_step_instances", type_="foreignkey")
    op.drop_constraint("fk_wf_step_inst_wf_inst_id_wf_insts", "workflow_step_instances", type_="foreignkey")
    op.drop_index("ix_workflow_step_instances_status", table_name="workflow_step_instances")
    op.drop_index("ix_workflow_step_instances_assigned_to_id", table_name="workflow_step_instances")
    op.drop_index("ix_workflow_step_instances_workflow_step_id", table_name="workflow_step_instances")
    op.drop_index("ix_workflow_step_instances_workflow_instance_id", table_name="workflow_step_instances")
    op.drop_table("workflow_step_instances")
