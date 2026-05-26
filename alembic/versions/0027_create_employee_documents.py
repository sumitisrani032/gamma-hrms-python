"""create employee documents table (Rails: 20260414070011_create_employee_documents)

Revision ID: 0027
Revises: 0026
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0027"
down_revision = "0026"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "employee_documents",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("attachment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_type", sa.String(length=50), nullable=False),
        sa.Column("document_name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("verified_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index("ix_emp_docs_tenant_id", "employee_documents", ["tenant_id"], unique=False)
    op.create_index("ix_emp_docs_employee_id", "employee_documents", ["employee_id"], unique=False)
    op.create_index("ix_emp_docs_attachment_id", "employee_documents", ["attachment_id"], unique=False)
    op.create_index("ix_emp_docs_document_type", "employee_documents", ["document_type"], unique=False)

    op.create_foreign_key(
        "fk_emp_docs_tenant_id_tenants",
        "employee_documents",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete=None,
    )
    op.create_foreign_key(
        "fk_emp_docs_employee_id_emps",
        "employee_documents",
        "employees",
        ["employee_id"],
        ["id"],
        ondelete=None,
    )
    op.create_foreign_key(
        "fk_emp_docs_attachment_id_atts",
        "employee_documents",
        "attachments",
        ["attachment_id"],
        ["id"],
        ondelete=None,
    )
    op.create_foreign_key(
        "fk_emp_docs_verified_by_id_users",
        "employee_documents",
        "users",
        ["verified_by_id"],
        ["id"],
        ondelete=None,
    )

    # RLS policy for table `employee_documents` using current_tenant_id()
    op.execute("ALTER TABLE employee_documents ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE employee_documents FORCE ROW LEVEL SECURITY;")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_policies
                WHERE schemaname = 'public'
                  AND tablename = 'employee_documents'
                  AND policyname = 'tenant_isolation_policy'
            ) THEN
                CREATE POLICY tenant_isolation_policy
                ON employee_documents
                USING (tenant_id = current_tenant_id());
            END IF;
        END;
        $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON employee_documents;")
    op.execute("ALTER TABLE employee_documents DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_emp_docs_verified_by_id_users", "employee_documents", type_="foreignkey")
    op.drop_constraint("fk_emp_docs_attachment_id_atts", "employee_documents", type_="foreignkey")
    op.drop_constraint("fk_emp_docs_employee_id_emps", "employee_documents", type_="foreignkey")
    op.drop_constraint("fk_emp_docs_tenant_id_tenants", "employee_documents", type_="foreignkey")
    op.drop_index("ix_emp_docs_document_type", table_name="employee_documents")
    op.drop_index("ix_emp_docs_attachment_id", table_name="employee_documents")
    op.drop_index("ix_emp_docs_employee_id", table_name="employee_documents")
    op.drop_index("ix_emp_docs_tenant_id", table_name="employee_documents")
    op.drop_table("employee_documents")
