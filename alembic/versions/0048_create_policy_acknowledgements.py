"""create policy acknowledgements table (Rails: 20260415100002_create_policy_acknowledgements)

Revision ID: 0048
Revises: 0047
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0048"
down_revision = "0047"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "policy_acknowledgements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("policy_document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("acknowledged_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("ip_address", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
    )

    op.create_index("ix_policy_acks_tenant_id", "policy_acknowledgements", ["tenant_id"])
    op.create_index("ix_policy_acks_policy_doc_id", "policy_acknowledgements", ["policy_document_id"])
    op.create_index("ix_policy_acks_employee_id", "policy_acknowledgements", ["employee_id"])
    op.create_index("ix_policy_acks_status", "policy_acknowledgements", ["status"])
    op.create_index("idx_policy_acks_unique", "policy_acknowledgements", ["tenant_id", "policy_document_id", "employee_id"], unique=True)

    op.create_foreign_key("fk_policy_acks_tenant_id_tenants", "policy_acknowledgements", "tenants", ["tenant_id"], ["id"])
    op.create_foreign_key("fk_policy_acks_pol_doc_id_docs", "policy_acknowledgements", "policy_documents", ["policy_document_id"], ["id"])
    op.create_foreign_key("fk_policy_acks_employee_id_emps", "policy_acknowledgements", "employees", ["employee_id"], ["id"])

    op.execute("ALTER TABLE policy_acknowledgements ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE policy_acknowledgements FORCE ROW LEVEL SECURITY;")
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname='public' AND tablename='policy_acknowledgements' AND policyname='tenant_isolation_policy') THEN
                CREATE POLICY tenant_isolation_policy ON policy_acknowledgements USING (tenant_id = current_tenant_id());
            END IF;
        END; $$;
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON policy_acknowledgements;")
    op.execute("ALTER TABLE policy_acknowledgements DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_policy_acks_employee_id_emps", "policy_acknowledgements", type_="foreignkey")
    op.drop_constraint("fk_policy_acks_pol_doc_id_docs", "policy_acknowledgements", type_="foreignkey")
    op.drop_constraint("fk_policy_acks_tenant_id_tenants", "policy_acknowledgements", type_="foreignkey")
    op.drop_index("idx_policy_acks_unique", table_name="policy_acknowledgements")
    op.drop_index("ix_policy_acks_status", table_name="policy_acknowledgements")
    op.drop_index("ix_policy_acks_employee_id", table_name="policy_acknowledgements")
    op.drop_index("ix_policy_acks_policy_doc_id", table_name="policy_acknowledgements")
    op.drop_index("ix_policy_acks_tenant_id", table_name="policy_acknowledgements")
    op.drop_table("policy_acknowledgements")
