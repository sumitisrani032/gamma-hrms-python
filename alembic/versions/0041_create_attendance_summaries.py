"""create attendance summaries table (Rails: 20260414070025_create_attendance_summaries)

Revision ID: 0041
Revises: 0040
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0041"
down_revision = "0040"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "attendance_summaries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("total_working_days", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("days_present", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("days_absent", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("days_half_day", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("days_on_leave", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("days_holiday", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("days_weekly_off", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_hours_worked", sa.Numeric(precision=7, scale=2), nullable=False, server_default=sa.text("0")),
        sa.Column("total_overtime_hours", sa.Numeric(precision=7, scale=2), nullable=False, server_default=sa.text("0")),
        sa.Column("late_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("early_exit_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
    )

    op.create_index("ix_att_summaries_tenant_id", "attendance_summaries", ["tenant_id"])
    op.create_index("ix_att_summaries_employee_id", "attendance_summaries", ["employee_id"])
    op.create_index("idx_attendance_summaries_unique", "attendance_summaries", ["tenant_id", "employee_id", "year", "month"], unique=True)

    op.create_foreign_key("fk_att_sums_tenant_id_tenants", "attendance_summaries", "tenants", ["tenant_id"], ["id"])
    op.create_foreign_key("fk_att_sums_employee_id_emps", "attendance_summaries", "employees", ["employee_id"], ["id"])

    op.execute("ALTER TABLE attendance_summaries ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE attendance_summaries FORCE ROW LEVEL SECURITY;")
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname='public' AND tablename='attendance_summaries' AND policyname='tenant_isolation_policy') THEN
                CREATE POLICY tenant_isolation_policy ON attendance_summaries USING (tenant_id = current_tenant_id());
            END IF;
        END; $$;
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON attendance_summaries;")
    op.execute("ALTER TABLE attendance_summaries DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_att_sums_employee_id_emps", "attendance_summaries", type_="foreignkey")
    op.drop_constraint("fk_att_sums_tenant_id_tenants", "attendance_summaries", type_="foreignkey")
    op.drop_index("idx_attendance_summaries_unique", table_name="attendance_summaries")
    op.drop_index("ix_att_summaries_employee_id", table_name="attendance_summaries")
    op.drop_index("ix_att_summaries_tenant_id", table_name="attendance_summaries")
    op.drop_table("attendance_summaries")
