"""create workflow instances table (Rails: 20260413070003_create_workflow_instances)

Revision ID: 0012
Revises: 0011
Create Date: 2026-05-25
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workflow_instances",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("workflow_definition_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.String(length=100), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("initiated_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("current_step_order", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("completed_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index("ix_workflow_instances_workflow_definition_id", "workflow_instances", ["workflow_definition_id"], unique=False)
    op.create_index("ix_workflow_instances_tenant_id", "workflow_instances", ["tenant_id"], unique=False)
    op.create_index("ix_workflow_instances_initiated_by_id", "workflow_instances", ["initiated_by_id"], unique=False)
    op.create_index("idx_workflow_instances_entity", "workflow_instances", ["entity_type", "entity_id"], unique=False)
    op.create_index("ix_workflow_instances_status", "workflow_instances", ["status"], unique=False)

    op.create_foreign_key(
        "fk_wf_instances_wf_def_id_wf_defs",
        "workflow_instances",
        "workflow_definitions",
        ["workflow_definition_id"],
        ["id"],
        ondelete=None,
    )
    op.create_foreign_key(
        "fk_wf_instances_tenant_id_tenants",
        "workflow_instances",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete=None,
    )
    op.create_foreign_key(
        "fk_wf_instances_initiated_by_id_users",
        "workflow_instances",
        "users",
        ["initiated_by_id"],
        ["id"],
        ondelete=None,
    )

    # RLS policy for table `workflow_instances` using current_tenant_id()
    op.execute("ALTER TABLE workflow_instances ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE workflow_instances FORCE ROW LEVEL SECURITY;")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_policies
                WHERE schemaname = 'public'
                  AND tablename = 'workflow_instances'
                  AND policyname = 'tenant_isolation_policy'
            ) THEN
                CREATE POLICY tenant_isolation_policy
                ON workflow_instances
                USING (tenant_id = current_tenant_id());
            END IF;
        END;
        $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON workflow_instances;")
    op.execute("ALTER TABLE workflow_instances DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_wf_instances_initiated_by_id_users", "workflow_instances", type_="foreignkey")
    op.drop_constraint("fk_wf_instances_tenant_id_tenants", "workflow_instances", type_="foreignkey")
    op.drop_constraint("fk_wf_instances_wf_def_id_wf_defs", "workflow_instances", type_="foreignkey")
    op.drop_index("ix_workflow_instances_status", table_name="workflow_instances")
    op.drop_index("idx_workflow_instances_entity", table_name="workflow_instances")
    op.drop_index("ix_workflow_instances_initiated_by_id", table_name="workflow_instances")
    op.drop_index("ix_workflow_instances_tenant_id", table_name="workflow_instances")
    op.drop_index("ix_workflow_instances_workflow_definition_id", table_name="workflow_instances")
    op.drop_table("workflow_instances")
