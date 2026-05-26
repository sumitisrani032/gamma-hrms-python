"""create policy documents table (Rails: 20260415100001_create_policy_documents)

Revision ID: 0047
Revises: 0046
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0047"
down_revision = "0046"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "policy_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("attachment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("published_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("previous_version_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'draft'")),
        sa.Column("acknowledgement_required", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("effective_date", sa.Date(), nullable=True),
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("version_number", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("applicable_to", sa.String(length=20), nullable=False, server_default=sa.text("'all'")),
        sa.Column("applicable_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("published_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
    )

    op.create_index("ix_policy_docs_tenant_id", "policy_documents", ["tenant_id"])
    op.create_index("ix_policy_docs_category", "policy_documents", ["category"])
    op.create_index("ix_policy_docs_status", "policy_documents", ["status"])
    op.create_index("idx_policy_docs_tenant_title_version", "policy_documents", ["tenant_id", "title", "version_number"], unique=True)

    op.create_foreign_key("fk_policy_docs_tenant_id_tenants", "policy_documents", "tenants", ["tenant_id"], ["id"])
    op.create_foreign_key("fk_policy_docs_attach_id_atts", "policy_documents", "attachments", ["attachment_id"], ["id"])
    op.create_foreign_key("fk_policy_docs_pub_by_id_users", "policy_documents", "users", ["published_by_id"], ["id"])
    op.create_foreign_key("fk_policy_docs_prev_ver_id_self", "policy_documents", "policy_documents", ["previous_version_id"], ["id"])

    op.execute("ALTER TABLE policy_documents ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE policy_documents FORCE ROW LEVEL SECURITY;")
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname='public' AND tablename='policy_documents' AND policyname='tenant_isolation_policy') THEN
                CREATE POLICY tenant_isolation_policy ON policy_documents USING (tenant_id = current_tenant_id());
            END IF;
        END; $$;
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON policy_documents;")
    op.execute("ALTER TABLE policy_documents DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_policy_docs_prev_ver_id_self", "policy_documents", type_="foreignkey")
    op.drop_constraint("fk_policy_docs_pub_by_id_users", "policy_documents", type_="foreignkey")
    op.drop_constraint("fk_policy_docs_attach_id_atts", "policy_documents", type_="foreignkey")
    op.drop_constraint("fk_policy_docs_tenant_id_tenants", "policy_documents", type_="foreignkey")
    op.drop_index("idx_policy_docs_tenant_title_version", table_name="policy_documents")
    op.drop_index("ix_policy_docs_status", table_name="policy_documents")
    op.drop_index("ix_policy_docs_category", table_name="policy_documents")
    op.drop_index("ix_policy_docs_tenant_id", table_name="policy_documents")
    op.drop_table("policy_documents")
