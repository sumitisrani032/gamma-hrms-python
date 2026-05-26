"""create employees table (Rails: 20260414070007_create_employees)

Revision ID: 0023
Revises: 0022
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0023"
down_revision = "0022"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "employees",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("department_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("designation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("grade_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("location_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("business_unit_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reporting_manager_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("employee_number", sa.String(length=50), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("middle_name", sa.String(length=100), nullable=True),
        sa.Column("email_official", sa.String(length=255), nullable=False),
        sa.Column("email_personal", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("gender", sa.String(length=20), nullable=True),
        sa.Column("marital_status", sa.String(length=20), nullable=True),
        sa.Column("blood_group", sa.String(length=10), nullable=True),
        sa.Column("nationality", sa.String(length=50), nullable=True, server_default=sa.text("'Indian'")),
        sa.Column("profile_photo_url", sa.Text(), nullable=True),
        sa.Column("date_of_joining", sa.Date(), nullable=False),
        sa.Column("date_of_confirmation", sa.Date(), nullable=True),
        sa.Column("probation_end_date", sa.Date(), nullable=True),
        sa.Column("date_of_exit", sa.Date(), nullable=True),
        sa.Column("notice_period_days", sa.Integer(), nullable=True, server_default=sa.text("0")),
        sa.Column("employment_type", sa.String(length=20), nullable=False, server_default=sa.text("'full_time'")),
        sa.Column("employment_status", sa.String(length=20), nullable=False, server_default=sa.text("'active'")),
        sa.Column("exit_reason", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'active'")),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index("ix_employees_tenant_id", "employees", ["tenant_id"], unique=False)
    op.create_index("ix_employees_user_id", "employees", ["user_id"], unique=False)
    op.create_index("ix_employees_company_id", "employees", ["company_id"], unique=False)
    op.create_index("ix_employees_department_id", "employees", ["department_id"], unique=False)
    op.create_index("ix_employees_designation_id", "employees", ["designation_id"], unique=False)
    op.create_index("ix_employees_grade_id", "employees", ["grade_id"], unique=False)
    op.create_index("ix_employees_location_id", "employees", ["location_id"], unique=False)
    op.create_index("ix_employees_business_unit_id", "employees", ["business_unit_id"], unique=False)
    op.create_index("ix_employees_reporting_manager_id", "employees", ["reporting_manager_id"], unique=False)
    
    op.create_index("uq_employees_tenant_emp_no", "employees", ["tenant_id", "employee_number"], unique=True)
    op.create_index("uq_employees_tenant_user_id", "employees", ["tenant_id", "user_id"], unique=True)
    op.create_index("ix_employees_employment_status", "employees", ["employment_status"], unique=False)
    op.create_index("ix_employees_date_of_joining", "employees", ["date_of_joining"], unique=False)

    op.create_foreign_key("fk_emp_tenant_id_tenants", "employees", "tenants", ["tenant_id"], ["id"], ondelete=None)
    op.create_foreign_key("fk_emp_user_id_users", "employees", "users", ["user_id"], ["id"], ondelete=None)
    op.create_foreign_key("fk_emp_company_id_companies", "employees", "companies", ["company_id"], ["id"], ondelete=None)
    op.create_foreign_key("fk_emp_department_id_depts", "employees", "departments", ["department_id"], ["id"], ondelete=None)
    op.create_foreign_key("fk_emp_designation_id_desigs", "employees", "designations", ["designation_id"], ["id"], ondelete=None)
    op.create_foreign_key("fk_emp_grade_id_grades", "employees", "grades", ["grade_id"], ["id"], ondelete=None)
    op.create_foreign_key("fk_emp_location_id_locs", "employees", "locations", ["location_id"], ["id"], ondelete=None)
    op.create_foreign_key("fk_emp_bus_unit_id_bus_units", "employees", "business_units", ["business_unit_id"], ["id"], ondelete=None)
    op.create_foreign_key("fk_emp_rep_mgr_id_emps", "employees", "employees", ["reporting_manager_id"], ["id"], ondelete=None)

    # RLS policy for table `employees` using current_tenant_id()
    op.execute("ALTER TABLE employees ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE employees FORCE ROW LEVEL SECURITY;")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_policies
                WHERE schemaname = 'public'
                  AND tablename = 'employees'
                  AND policyname = 'tenant_isolation_policy'
            ) THEN
                CREATE POLICY tenant_isolation_policy
                ON employees
                USING (tenant_id = current_tenant_id());
            END IF;
        END;
        $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON employees;")
    op.execute("ALTER TABLE employees DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_emp_rep_mgr_id_emps", "employees", type_="foreignkey")
    op.drop_constraint("fk_emp_bus_unit_id_bus_units", "employees", type_="foreignkey")
    op.drop_constraint("fk_emp_location_id_locs", "employees", type_="foreignkey")
    op.drop_constraint("fk_emp_grade_id_grades", "employees", type_="foreignkey")
    op.drop_constraint("fk_emp_designation_id_desigs", "employees", type_="foreignkey")
    op.drop_constraint("fk_emp_department_id_depts", "employees", type_="foreignkey")
    op.drop_constraint("fk_emp_company_id_companies", "employees", type_="foreignkey")
    op.drop_constraint("fk_emp_user_id_users", "employees", type_="foreignkey")
    op.drop_constraint("fk_emp_tenant_id_tenants", "employees", type_="foreignkey")
    op.drop_index("ix_employees_date_of_joining", table_name="employees")
    op.drop_index("ix_employees_employment_status", table_name="employees")
    op.drop_index("uq_employees_tenant_user_id", table_name="employees")
    op.drop_index("uq_employees_tenant_emp_no", table_name="employees")
    op.drop_index("ix_employees_reporting_manager_id", table_name="employees")
    op.drop_index("ix_employees_business_unit_id", table_name="employees")
    op.drop_index("ix_employees_location_id", table_name="employees")
    op.drop_index("ix_employees_grade_id", table_name="employees")
    op.drop_index("ix_employees_designation_id", table_name="employees")
    op.drop_index("ix_employees_department_id", table_name="employees")
    op.drop_index("ix_employees_company_id", table_name="employees")
    op.drop_index("ix_employees_user_id", table_name="employees")
    op.drop_index("ix_employees_tenant_id", table_name="employees")
    op.drop_table("employees")
