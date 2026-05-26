"""create workflow definitions table (Rails: 20260413070001_create_workflow_definitions)

Revision ID: 0010
Revises: 0009
Create Date: 2026-05-25
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workflow_definitions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("entity_type", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index("ix_workflow_definitions_tenant_id", "workflow_definitions", ["tenant_id"], unique=False)
    op.create_index("idx_workflow_defs_tenant_entity", "workflow_definitions", ["tenant_id", "entity_type"], unique=False)

    op.create_foreign_key(
        "fk_workflow_definitions_tenant_id_tenants",
        "workflow_definitions",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete=None,
    )

    # RLS policy for table `workflow_definitions` using current_tenant_id()
    op.execute("ALTER TABLE workflow_definitions ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE workflow_definitions FORCE ROW LEVEL SECURITY;")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_policies
                WHERE schemaname = 'public'
                  AND tablename = 'workflow_definitions'
                  AND policyname = 'tenant_isolation_policy'
            ) THEN
                CREATE POLICY tenant_isolation_policy
                ON workflow_definitions
                USING (tenant_id = current_tenant_id());
            END IF;
        END;
        $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON workflow_definitions;")
    op.execute("ALTER TABLE workflow_definitions DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_workflow_definitions_tenant_id_tenants", "workflow_definitions", type_="foreignkey")
    op.drop_index("idx_workflow_defs_tenant_entity", table_name="workflow_definitions")
    op.drop_index("ix_workflow_definitions_tenant_id", table_name="workflow_definitions")
    op.drop_table("workflow_definitions")
