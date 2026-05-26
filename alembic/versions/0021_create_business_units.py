"""create business units table (Rails: 20260414070005_create_business_units)

Revision ID: 0021
Revises: 0020
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0021"
down_revision = "0020"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "business_units",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("head_employee_id", postgresql.UUID(as_uuid=True), nullable=True), # Note: FK constraint added in later migration
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'active'")),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index("ix_business_units_tenant_id", "business_units", ["tenant_id"], unique=False)
    op.create_index("ix_business_units_company_id", "business_units", ["company_id"], unique=False)
    op.create_index("uq_business_units_tenant_name", "business_units", ["tenant_id", "name"], unique=True)

    op.create_foreign_key(
        "fk_business_units_tenant_id_tenants",
        "business_units",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete=None,
    )
    op.create_foreign_key(
        "fk_business_units_company_id_companies",
        "business_units",
        "companies",
        ["company_id"],
        ["id"],
        ondelete=None,
    )

    # RLS policy for table `business_units` using current_tenant_id()
    op.execute("ALTER TABLE business_units ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE business_units FORCE ROW LEVEL SECURITY;")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_policies
                WHERE schemaname = 'public'
                  AND tablename = 'business_units'
                  AND policyname = 'tenant_isolation_policy'
            ) THEN
                CREATE POLICY tenant_isolation_policy
                ON business_units
                USING (tenant_id = current_tenant_id());
            END IF;
        END;
        $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON business_units;")
    op.execute("ALTER TABLE business_units DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_business_units_company_id_companies", "business_units", type_="foreignkey")
    op.drop_constraint("fk_business_units_tenant_id_tenants", "business_units", type_="foreignkey")
    op.drop_index("uq_business_units_tenant_name", table_name="business_units")
    op.drop_index("ix_business_units_company_id", table_name="business_units")
    op.drop_index("ix_business_units_tenant_id", table_name="business_units")
    op.drop_table("business_units")
