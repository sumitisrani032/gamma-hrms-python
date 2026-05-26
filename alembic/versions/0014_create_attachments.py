"""create attachments table (Rails: 20260413070005_create_attachments)

Revision ID: 0014
Revises: 0013
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0014"
down_revision = "0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "attachments",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("uploaded_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_type", sa.String(length=50), nullable=True),
        sa.Column("file_size", sa.BigInteger(), nullable=True),
        sa.Column("s3_key", sa.Text(), nullable=False),
        sa.Column("entity_type", sa.String(length=100), nullable=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index("ix_attachments_tenant_id", "attachments", ["tenant_id"], unique=False)
    op.create_index("ix_attachments_uploaded_by_id", "attachments", ["uploaded_by_id"], unique=False)
    op.create_index("idx_attachments_entity", "attachments", ["entity_type", "entity_id"], unique=False)

    op.create_foreign_key(
        "fk_attachments_tenant_id_tenants",
        "attachments",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete=None,
    )
    op.create_foreign_key(
        "fk_attachments_uploaded_by_id_users",
        "attachments",
        "users",
        ["uploaded_by_id"],
        ["id"],
        ondelete=None,
    )

    # RLS policy for table `attachments` using current_tenant_id()
    op.execute("ALTER TABLE attachments ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE attachments FORCE ROW LEVEL SECURITY;")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_policies
                WHERE schemaname = 'public'
                  AND tablename = 'attachments'
                  AND policyname = 'tenant_isolation_policy'
            ) THEN
                CREATE POLICY tenant_isolation_policy
                ON attachments
                USING (tenant_id = current_tenant_id());
            END IF;
        END;
        $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON attachments;")
    op.execute("ALTER TABLE attachments DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_attachments_uploaded_by_id_users", "attachments", type_="foreignkey")
    op.drop_constraint("fk_attachments_tenant_id_tenants", "attachments", type_="foreignkey")
    op.drop_index("idx_attachments_entity", table_name="attachments")
    op.drop_index("ix_attachments_uploaded_by_id", table_name="attachments")
    op.drop_index("ix_attachments_tenant_id", table_name="attachments")
    op.drop_table("attachments")
