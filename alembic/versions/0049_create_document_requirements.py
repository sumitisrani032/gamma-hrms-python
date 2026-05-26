"""create document requirements table (Rails: 20260415100003_create_document_requirements)

Revision ID: 0049
Revises: 0048
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0049"
down_revision = "0048"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "document_requirements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("document_type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_mandatory", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("applicable_to", sa.String(length=20), nullable=False, server_default=sa.text("'all'")),
        sa.Column("applicable_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("has_expiry", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("allowed_file_types", sa.String(length=255), nullable=True),
        sa.Column("max_file_size_mb", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
    )

    op.create_index("ix_doc_reqs_tenant_id", "document_requirements", ["tenant_id"])
    op.create_index("ix_doc_reqs_document_type", "document_requirements", ["document_type"])
    op.create_index("idx_doc_requirements_tenant_name", "document_requirements", ["tenant_id", "name"], unique=True)

    op.create_foreign_key("fk_doc_reqs_tenant_id_tenants", "document_requirements", "tenants", ["tenant_id"], ["id"])

    op.execute("ALTER TABLE document_requirements ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE document_requirements FORCE ROW LEVEL SECURITY;")
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname='public' AND tablename='document_requirements' AND policyname='tenant_isolation_policy') THEN
                CREATE POLICY tenant_isolation_policy ON document_requirements USING (tenant_id = current_tenant_id());
            END IF;
        END; $$;
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON document_requirements;")
    op.execute("ALTER TABLE document_requirements DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_doc_reqs_tenant_id_tenants", "document_requirements", type_="foreignkey")
    op.drop_index("idx_doc_requirements_tenant_name", table_name="document_requirements")
    op.drop_index("ix_doc_reqs_document_type", table_name="document_requirements")
    op.drop_index("ix_doc_reqs_tenant_id", table_name="document_requirements")
    op.drop_table("document_requirements")
