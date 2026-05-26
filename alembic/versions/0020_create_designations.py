"""create designations table (Rails: 20260414070004_create_designations)

Revision ID: 0020
Revises: 0019
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0020"
down_revision = "0019"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "designations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=True),
        sa.Column("level", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'active'")),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index("ix_designations_tenant_id", "designations", ["tenant_id"], unique=False)
    op.create_index("uq_designations_tenant_name", "designations", ["tenant_id", "name"], unique=True)

    op.create_foreign_key(
        "fk_designations_tenant_id_tenants",
        "designations",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete=None,
    )

    # RLS policy for table `designations` using current_tenant_id()
    op.execute("ALTER TABLE designations ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE designations FORCE ROW LEVEL SECURITY;")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_policies
                WHERE schemaname = 'public'
                  AND tablename = 'designations'
                  AND policyname = 'tenant_isolation_policy'
            ) THEN
                CREATE POLICY tenant_isolation_policy
                ON designations
                USING (tenant_id = current_tenant_id());
            END IF;
        END;
        $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON designations;")
    op.execute("ALTER TABLE designations DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_designations_tenant_id_tenants", "designations", type_="foreignkey")
    op.drop_index("uq_designations_tenant_name", table_name="designations")
    op.drop_index("ix_designations_tenant_id", table_name="designations")
    op.drop_table("designations")
