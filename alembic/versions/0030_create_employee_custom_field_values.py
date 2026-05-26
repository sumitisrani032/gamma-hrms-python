"""create employee custom field values table (Rails: 20260414070014_create_employee_custom_field_values)

Revision ID: 0030
Revises: 0029
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0030"
down_revision = "0029"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "employee_custom_field_values",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("field_definition_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("value", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index("ix_emp_cf_vals_tenant_id", "employee_custom_field_values", ["tenant_id"], unique=False)
    op.create_index("ix_emp_cf_vals_employee_id", "employee_custom_field_values", ["employee_id"], unique=False)
    op.create_index("ix_emp_cf_vals_field_def_id", "employee_custom_field_values", ["field_definition_id"], unique=False)
    op.create_index("idx_emp_custom_values_unique", "employee_custom_field_values", ["tenant_id", "employee_id", "field_definition_id"], unique=True)

    op.create_foreign_key(
        "fk_emp_cf_vals_tenant_id_tenants",
        "employee_custom_field_values",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete=None,
    )
    op.create_foreign_key(
        "fk_emp_cf_vals_employee_id_emps",
        "employee_custom_field_values",
        "employees",
        ["employee_id"],
        ["id"],
        ondelete=None,
    )
    op.create_foreign_key(
        "fk_emp_cf_vals_field_def_id_defs",
        "employee_custom_field_values",
        "employee_custom_field_definitions",
        ["field_definition_id"],
        ["id"],
        ondelete=None,
    )

    # RLS policy for table `employee_custom_field_values` using current_tenant_id()
    op.execute("ALTER TABLE employee_custom_field_values ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE employee_custom_field_values FORCE ROW LEVEL SECURITY;")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_policies
                WHERE schemaname = 'public'
                  AND tablename = 'employee_custom_field_values'
                  AND policyname = 'tenant_isolation_policy'
            ) THEN
                CREATE POLICY tenant_isolation_policy
                ON employee_custom_field_values
                USING (tenant_id = current_tenant_id());
            END IF;
        END;
        $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON employee_custom_field_values;")
    op.execute("ALTER TABLE employee_custom_field_values DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_emp_cf_vals_field_def_id_defs", "employee_custom_field_values", type_="foreignkey")
    op.drop_constraint("fk_emp_cf_vals_employee_id_emps", "employee_custom_field_values", type_="foreignkey")
    op.drop_constraint("fk_emp_cf_vals_tenant_id_tenants", "employee_custom_field_values", type_="foreignkey")
    op.drop_index("idx_emp_custom_values_unique", table_name="employee_custom_field_values")
    op.drop_index("ix_emp_cf_vals_field_def_id", table_name="employee_custom_field_values")
    op.drop_index("ix_emp_cf_vals_employee_id", table_name="employee_custom_field_values")
    op.drop_index("ix_emp_cf_vals_tenant_id", table_name="employee_custom_field_values")
    op.drop_table("employee_custom_field_values")
