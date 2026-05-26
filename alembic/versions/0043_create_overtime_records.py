"""create overtime records table (Rails: 20260414070027_create_overtime_records)

Revision ID: 0043
Revises: 0042
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0043"
down_revision = "0042"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "overtime_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("overtime_rule_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("overtime_hours", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("rate_multiplier", sa.Numeric(precision=4, scale=2), nullable=False),
        sa.Column("is_holiday_ot", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'computed'")),
        sa.Column("approved_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
    )

    op.create_index("ix_ot_records_tenant_id", "overtime_records", ["tenant_id"])
    op.create_index("ix_ot_records_employee_id", "overtime_records", ["employee_id"])
    op.create_index("ix_ot_records_ot_rule_id", "overtime_records", ["overtime_rule_id"])
    op.create_index("idx_overtime_records_unique", "overtime_records", ["tenant_id", "employee_id", "date"], unique=True)
    op.create_index("ix_ot_records_status", "overtime_records", ["status"])

    op.create_foreign_key("fk_ot_records_tenant_id_tenants", "overtime_records", "tenants", ["tenant_id"], ["id"])
    op.create_foreign_key("fk_ot_records_employee_id_emps", "overtime_records", "employees", ["employee_id"], ["id"])
    op.create_foreign_key("fk_ot_records_ot_rule_id_ot_rules", "overtime_records", "overtime_rules", ["overtime_rule_id"], ["id"])
    op.create_foreign_key("fk_ot_records_appr_by_id_users", "overtime_records", "users", ["approved_by_id"], ["id"])

    op.execute("ALTER TABLE overtime_records ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE overtime_records FORCE ROW LEVEL SECURITY;")
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname='public' AND tablename='overtime_records' AND policyname='tenant_isolation_policy') THEN
                CREATE POLICY tenant_isolation_policy ON overtime_records USING (tenant_id = current_tenant_id());
            END IF;
        END; $$;
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON overtime_records;")
    op.execute("ALTER TABLE overtime_records DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_ot_records_appr_by_id_users", "overtime_records", type_="foreignkey")
    op.drop_constraint("fk_ot_records_ot_rule_id_ot_rules", "overtime_records", type_="foreignkey")
    op.drop_constraint("fk_ot_records_employee_id_emps", "overtime_records", type_="foreignkey")
    op.drop_constraint("fk_ot_records_tenant_id_tenants", "overtime_records", type_="foreignkey")
    op.drop_index("ix_ot_records_status", table_name="overtime_records")
    op.drop_index("idx_overtime_records_unique", table_name="overtime_records")
    op.drop_index("ix_ot_records_ot_rule_id", table_name="overtime_records")
    op.drop_index("ix_ot_records_employee_id", table_name="overtime_records")
    op.drop_index("ix_ot_records_tenant_id", table_name="overtime_records")
    op.drop_table("overtime_records")
