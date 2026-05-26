"""create employee custom field definitions table (Rails: 20260414070013_create_employee_custom_field_definitions)

Revision ID: 0029
Revises: 0028
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0029"
down_revision = "0028"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "employee_custom_field_definitions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("field_name", sa.String(length=255), nullable=False),
        sa.Column("field_key", sa.String(length=100), nullable=False),
        sa.Column("field_type", sa.String(length=20), nullable=False),
        sa.Column("options", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("is_required", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("section", sa.String(length=50), nullable=True, server_default=sa.text("'custom'")),
        sa.Column("display_order", sa.Integer(), nullable=True, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index("ix_emp_cf_defs_tenant_id", "employee_custom_field_definitions", ["tenant_id"], unique=False)
    op.create_index("idx_emp_custom_fields_tenant_key", "employee_custom_field_definitions", ["tenant_id", "field_key"], unique=True)

    op.create_foreign_key(
        "fk_emp_cf_defs_tenant_id_tenants",
        "employee_custom_field_definitions",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete=None,
    )

    # RLS policy for table `employee_custom_field_definitions` using current_tenant_id()
    op.execute("ALTER TABLE employee_custom_field_definitions ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE employee_custom_field_definitions FORCE ROW LEVEL SECURITY;")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_policies
                WHERE schemaname = 'public'
                  AND tablename = 'employee_custom_field_definitions'
                  AND policyname = 'tenant_isolation_policy'
            ) THEN
                CREATE POLICY tenant_isolation_policy
                ON employee_custom_field_definitions
                USING (tenant_id = current_tenant_id());
            END IF;
        END;
        $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON employee_custom_field_definitions;")
    op.execute("ALTER TABLE employee_custom_field_definitions DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_emp_cf_defs_tenant_id_tenants", "employee_custom_field_definitions", type_="foreignkey")
    op.drop_index("idx_emp_custom_fields_tenant_key", table_name="employee_custom_field_definitions")
    op.drop_index("ix_emp_cf_defs_tenant_id", table_name="employee_custom_field_definitions")
    op.drop_table("employee_custom_field_definitions")
