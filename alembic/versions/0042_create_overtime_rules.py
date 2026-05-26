"""create overtime rules table (Rails: 20260414070026_create_overtime_rules)

Revision ID: 0042
Revises: 0041
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0042"
down_revision = "0041"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "overtime_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("threshold_hours", sa.Numeric(precision=4, scale=2), nullable=False),
        sa.Column("rate_multiplier", sa.Numeric(precision=4, scale=2), nullable=False, server_default=sa.text("1.5")),
        sa.Column("max_daily_ot_hours", sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column("max_monthly_ot_hours", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("applicable_on_holidays", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("holiday_rate_multiplier", sa.Numeric(precision=4, scale=2), nullable=True, server_default=sa.text("2.0")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
    )

    op.create_index("ix_ot_rules_tenant_id", "overtime_rules", ["tenant_id"])
    op.create_index("idx_overtime_rules_unique", "overtime_rules", ["tenant_id", "name"], unique=True)

    op.create_foreign_key("fk_ot_rules_tenant_id_tenants", "overtime_rules", "tenants", ["tenant_id"], ["id"])

    op.execute("ALTER TABLE overtime_rules ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE overtime_rules FORCE ROW LEVEL SECURITY;")
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname='public' AND tablename='overtime_rules' AND policyname='tenant_isolation_policy') THEN
                CREATE POLICY tenant_isolation_policy ON overtime_rules USING (tenant_id = current_tenant_id());
            END IF;
        END; $$;
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON overtime_rules;")
    op.execute("ALTER TABLE overtime_rules DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_ot_rules_tenant_id_tenants", "overtime_rules", type_="foreignkey")
    op.drop_index("idx_overtime_rules_unique", table_name="overtime_rules")
    op.drop_index("ix_ot_rules_tenant_id", table_name="overtime_rules")
    op.drop_table("overtime_rules")
