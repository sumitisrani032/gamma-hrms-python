"""create attendance records table (Rails: 20260414070023_create_attendance_records)

Revision ID: 0039
Revises: 0038
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0039"
down_revision = "0038"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "attendance_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("shift_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("clock_in", sa.DateTime(timezone=False), nullable=True),
        sa.Column("clock_out", sa.DateTime(timezone=False), nullable=True),
        sa.Column("total_hours", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("effective_hours", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'absent'")),
        sa.Column("source", sa.String(length=20), nullable=True, server_default=sa.text("'manual'")),
        sa.Column("is_late", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("late_minutes", sa.Integer(), nullable=True, server_default=sa.text("0")),
        sa.Column("is_early_departure", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("overtime_minutes", sa.Integer(), nullable=True, server_default=sa.text("0")),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("is_regularized", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
    )

    op.create_index("ix_att_records_tenant_id", "attendance_records", ["tenant_id"])
    op.create_index("ix_att_records_employee_id", "attendance_records", ["employee_id"])
    op.create_index("idx_attendance_records_unique", "attendance_records", ["tenant_id", "employee_id", "date"], unique=True)
    op.create_index("ix_att_records_status", "attendance_records", ["status"])
    op.create_index("ix_att_records_date", "attendance_records", ["date"])

    op.create_foreign_key("fk_att_records_tenant_id_tenants", "attendance_records", "tenants", ["tenant_id"], ["id"])
    op.create_foreign_key("fk_att_records_employee_id_emps", "attendance_records", "employees", ["employee_id"], ["id"])
    op.create_foreign_key("fk_att_records_shift_id_shifts", "attendance_records", "shifts", ["shift_id"], ["id"])

    op.execute("ALTER TABLE attendance_records ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE attendance_records FORCE ROW LEVEL SECURITY;")
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname='public' AND tablename='attendance_records' AND policyname='tenant_isolation_policy') THEN
                CREATE POLICY tenant_isolation_policy ON attendance_records USING (tenant_id = current_tenant_id());
            END IF;
        END; $$;
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON attendance_records;")
    op.execute("ALTER TABLE attendance_records DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_att_records_shift_id_shifts", "attendance_records", type_="foreignkey")
    op.drop_constraint("fk_att_records_employee_id_emps", "attendance_records", type_="foreignkey")
    op.drop_constraint("fk_att_records_tenant_id_tenants", "attendance_records", type_="foreignkey")
    op.drop_index("ix_att_records_date", table_name="attendance_records")
    op.drop_index("ix_att_records_status", table_name="attendance_records")
    op.drop_index("idx_attendance_records_unique", table_name="attendance_records")
    op.drop_index("ix_att_records_employee_id", table_name="attendance_records")
    op.drop_index("ix_att_records_tenant_id", table_name="attendance_records")
    op.drop_table("attendance_records")
