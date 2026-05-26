"""extend employee documents (Rails: 20260415100004_extend_employee_documents)

Revision ID: 0050
Revises: 0049
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0050"
down_revision = "0049"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("employee_documents", sa.Column("document_requirement_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("employee_documents", sa.Column("rejection_reason", sa.Text(), nullable=True))
    op.add_column("employee_documents", sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'pending'")))

    op.create_index("ix_emp_docs_status", "employee_documents", ["status"])
    op.create_index(
        "ix_emp_docs_doc_requirement_id",
        "employee_documents",
        ["document_requirement_id"],
    )
    # Partial unique index: only enforced when document_requirement_id is not null
    op.create_index(
        "idx_emp_docs_tenant_emp_req",
        "employee_documents",
        ["tenant_id", "employee_id", "document_requirement_id"],
        unique=True,
        postgresql_where=sa.text("document_requirement_id IS NOT NULL"),
    )

    op.create_foreign_key(
        "fk_emp_docs_doc_req_id_doc_reqs",
        "employee_documents",
        "document_requirements",
        ["document_requirement_id"],
        ["id"],
    )

    # Sync existing verified records
    op.execute("UPDATE employee_documents SET status = 'verified' WHERE verified = true")


def downgrade() -> None:
    op.drop_constraint("fk_emp_docs_doc_req_id_doc_reqs", "employee_documents", type_="foreignkey")
    op.drop_index("idx_emp_docs_tenant_emp_req", table_name="employee_documents")
    op.drop_index("ix_emp_docs_doc_requirement_id", table_name="employee_documents")
    op.drop_index("ix_emp_docs_status", table_name="employee_documents")
    op.drop_column("employee_documents", "status")
    op.drop_column("employee_documents", "rejection_reason")
    op.drop_column("employee_documents", "document_requirement_id")
