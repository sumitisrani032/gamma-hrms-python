"""create employee personal details table (Rails: 20260414070009_create_employee_personal_details)

Revision ID: 0025
Revises: 0024
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0025"
down_revision = "0024"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "employee_personal_details",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=False),
        
        # Current address
        sa.Column("current_address", sa.Text(), nullable=True),
        sa.Column("current_city", sa.String(length=100), nullable=True),
        sa.Column("current_state", sa.String(length=100), nullable=True),
        sa.Column("current_country", sa.String(length=100), nullable=True),
        sa.Column("current_pincode", sa.String(length=20), nullable=True),
        
        # Permanent address
        sa.Column("permanent_address", sa.Text(), nullable=True),
        sa.Column("permanent_city", sa.String(length=100), nullable=True),
        sa.Column("permanent_state", sa.String(length=100), nullable=True),
        sa.Column("permanent_country", sa.String(length=100), nullable=True),
        sa.Column("permanent_pincode", sa.String(length=20), nullable=True),
        
        # Emergency contact
        sa.Column("emergency_contact_name", sa.String(length=200), nullable=True),
        sa.Column("emergency_contact_phone", sa.String(length=20), nullable=True),
        sa.Column("emergency_contact_relation", sa.String(length=50), nullable=True),
        
        # Identity documents
        sa.Column("pan_number", sa.String(length=20), nullable=True),
        sa.Column("aadhaar_number", sa.String(length=20), nullable=True),
        sa.Column("passport_number", sa.String(length=20), nullable=True),
        sa.Column("passport_expiry", sa.Date(), nullable=True),
        sa.Column("uan_number", sa.String(length=20), nullable=True),
        
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index("ix_emp_personal_details_tenant_id", "employee_personal_details", ["tenant_id"], unique=False)
    op.create_index("ix_emp_personal_details_employee_id", "employee_personal_details", ["employee_id"], unique=False)
    op.create_index("idx_emp_personal_details_tenant_employee", "employee_personal_details", ["tenant_id", "employee_id"], unique=True)

    op.create_foreign_key(
        "fk_emp_pers_dtls_tenant_id_tenants",
        "employee_personal_details",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete=None,
    )
    op.create_foreign_key(
        "fk_emp_pers_dtls_employee_id_emps",
        "employee_personal_details",
        "employees",
        ["employee_id"],
        ["id"],
        ondelete=None,
    )

    # RLS policy for table `employee_personal_details` using current_tenant_id()
    op.execute("ALTER TABLE employee_personal_details ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE employee_personal_details FORCE ROW LEVEL SECURITY;")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_policies
                WHERE schemaname = 'public'
                  AND tablename = 'employee_personal_details'
                  AND policyname = 'tenant_isolation_policy'
            ) THEN
                CREATE POLICY tenant_isolation_policy
                ON employee_personal_details
                USING (tenant_id = current_tenant_id());
            END IF;
        END;
        $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON employee_personal_details;")
    op.execute("ALTER TABLE employee_personal_details DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_emp_pers_dtls_employee_id_emps", "employee_personal_details", type_="foreignkey")
    op.drop_constraint("fk_emp_pers_dtls_tenant_id_tenants", "employee_personal_details", type_="foreignkey")
    op.drop_index("idx_emp_personal_details_tenant_employee", table_name="employee_personal_details")
    op.drop_index("ix_emp_personal_details_employee_id", table_name="employee_personal_details")
    op.drop_index("ix_emp_personal_details_tenant_id", table_name="employee_personal_details")
    op.drop_table("employee_personal_details")
