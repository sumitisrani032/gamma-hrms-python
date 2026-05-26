"""create departments table (Rails: 20260414070006_create_departments)

Revision ID: 0022
Revises: 0021
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0022"
down_revision = "0021"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "departments",
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
        sa.Column("parent_department_id", postgresql.UUID(as_uuid=True), nullable=True),
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

    op.create_index("ix_departments_tenant_id", "departments", ["tenant_id"], unique=False)
    op.create_index("ix_departments_company_id", "departments", ["company_id"], unique=False)
    op.create_index("ix_departments_parent_department_id", "departments", ["parent_department_id"], unique=False)
    op.create_index("idx_departments_tenant_company_name", "departments", ["tenant_id", "company_id", "name"], unique=True)

    op.create_foreign_key(
        "fk_departments_tenant_id_tenants",
        "departments",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete=None,
    )
    op.create_foreign_key(
        "fk_departments_company_id_companies",
        "departments",
        "companies",
        ["company_id"],
        ["id"],
        ondelete=None,
    )
    op.create_foreign_key(
        "fk_departments_parent_department_id_departments",
        "departments",
        "departments",
        ["parent_department_id"],
        ["id"],
        ondelete=None,
    )

    # RLS policy for table `departments` using current_tenant_id()
    op.execute("ALTER TABLE departments ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE departments FORCE ROW LEVEL SECURITY;")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_policies
                WHERE schemaname = 'public'
                  AND tablename = 'departments'
                  AND policyname = 'tenant_isolation_policy'
            ) THEN
                CREATE POLICY tenant_isolation_policy
                ON departments
                USING (tenant_id = current_tenant_id());
            END IF;
        END;
        $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON departments;")
    op.execute("ALTER TABLE departments DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_departments_parent_department_id_departments", "departments", type_="foreignkey")
    op.drop_constraint("fk_departments_company_id_companies", "departments", type_="foreignkey")
    op.drop_constraint("fk_departments_tenant_id_tenants", "departments", type_="foreignkey")
    op.drop_index("idx_departments_tenant_company_name", table_name="departments")
    op.drop_index("ix_departments_parent_department_id", table_name="departments")
    op.drop_index("ix_departments_company_id", table_name="departments")
    op.drop_index("ix_departments_tenant_id", table_name="departments")
    op.drop_table("departments")
