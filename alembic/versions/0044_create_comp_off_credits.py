"""create comp off credits table (Rails: 20260414070028_create_comp_off_credits)

Revision ID: 0044
Revises: 0043
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0044"
down_revision = "0043"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "comp_off_credits",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("earned_date", sa.Date(), nullable=False),
        sa.Column("expires_at", sa.Date(), nullable=True),
        sa.Column("days_credited", sa.Numeric(precision=3, scale=1), nullable=False, server_default=sa.text("1.0")),
        sa.Column("days_used", sa.Numeric(precision=3, scale=1), nullable=False, server_default=sa.text("0")),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'active'")),
        sa.Column("approved_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
    )

    op.create_index("ix_comp_off_tenant_id", "comp_off_credits", ["tenant_id"])
    op.create_index("ix_comp_off_employee_id", "comp_off_credits", ["employee_id"])
    op.create_index("idx_comp_off_credits_employee", "comp_off_credits", ["tenant_id", "employee_id"])
    op.create_index("ix_comp_off_status", "comp_off_credits", ["status"])
    op.create_index("ix_comp_off_expires_at", "comp_off_credits", ["expires_at"])

    op.create_foreign_key("fk_comp_off_tenant_id_tenants", "comp_off_credits", "tenants", ["tenant_id"], ["id"])
    op.create_foreign_key("fk_comp_off_employee_id_emps", "comp_off_credits", "employees", ["employee_id"], ["id"])
    op.create_foreign_key("fk_comp_off_appr_by_id_users", "comp_off_credits", "users", ["approved_by_id"], ["id"])

    op.execute("ALTER TABLE comp_off_credits ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE comp_off_credits FORCE ROW LEVEL SECURITY;")
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname='public' AND tablename='comp_off_credits' AND policyname='tenant_isolation_policy') THEN
                CREATE POLICY tenant_isolation_policy ON comp_off_credits USING (tenant_id = current_tenant_id());
            END IF;
        END; $$;
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON comp_off_credits;")
    op.execute("ALTER TABLE comp_off_credits DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_comp_off_appr_by_id_users", "comp_off_credits", type_="foreignkey")
    op.drop_constraint("fk_comp_off_employee_id_emps", "comp_off_credits", type_="foreignkey")
    op.drop_constraint("fk_comp_off_tenant_id_tenants", "comp_off_credits", type_="foreignkey")
    op.drop_index("ix_comp_off_expires_at", table_name="comp_off_credits")
    op.drop_index("ix_comp_off_status", table_name="comp_off_credits")
    op.drop_index("idx_comp_off_credits_employee", table_name="comp_off_credits")
    op.drop_index("ix_comp_off_employee_id", table_name="comp_off_credits")
    op.drop_index("ix_comp_off_tenant_id", table_name="comp_off_credits")
    op.drop_table("comp_off_credits")
