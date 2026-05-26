"""create employee bank details table (Rails: 20260414070010_create_employee_bank_details)

Revision ID: 0026
Revises: 0025
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0026"
down_revision = "0025"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "employee_bank_details",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bank_name", sa.String(length=255), nullable=False),
        sa.Column("branch_name", sa.String(length=255), nullable=True),
        sa.Column("account_number", sa.String(length=50), nullable=False),
        sa.Column("ifsc_code", sa.String(length=20), nullable=False),
        sa.Column("account_type", sa.String(length=20), nullable=False, server_default=sa.text("'savings'")),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'active'")),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index("ix_emp_bank_details_tenant_id", "employee_bank_details", ["tenant_id"], unique=False)
    op.create_index("ix_emp_bank_details_employee_id", "employee_bank_details", ["employee_id"], unique=False)
    op.create_index("idx_emp_bank_tenant_employee_account", "employee_bank_details", ["tenant_id", "employee_id", "account_number"], unique=True)

    op.create_foreign_key(
        "fk_emp_bank_dtls_tenant_id_tenants",
        "employee_bank_details",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete=None,
    )
    op.create_foreign_key(
        "fk_emp_bank_dtls_employee_id_emps",
        "employee_bank_details",
        "employees",
        ["employee_id"],
        ["id"],
        ondelete=None,
    )

    # RLS policy for table `employee_bank_details` using current_tenant_id()
    op.execute("ALTER TABLE employee_bank_details ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE employee_bank_details FORCE ROW LEVEL SECURITY;")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_policies
                WHERE schemaname = 'public'
                  AND tablename = 'employee_bank_details'
                  AND policyname = 'tenant_isolation_policy'
            ) THEN
                CREATE POLICY tenant_isolation_policy
                ON employee_bank_details
                USING (tenant_id = current_tenant_id());
            END IF;
        END;
        $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON employee_bank_details;")
    op.execute("ALTER TABLE employee_bank_details DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_emp_bank_dtls_employee_id_emps", "employee_bank_details", type_="foreignkey")
    op.drop_constraint("fk_emp_bank_dtls_tenant_id_tenants", "employee_bank_details", type_="foreignkey")
    op.drop_index("idx_emp_bank_tenant_employee_account", table_name="employee_bank_details")
    op.drop_index("ix_emp_bank_details_employee_id", table_name="employee_bank_details")
    op.drop_index("ix_emp_bank_details_tenant_id", table_name="employee_bank_details")
    op.drop_table("employee_bank_details")
