"""create attendance sessions table (Rails: 20260415110001_create_attendance_sessions)

Revision ID: 0051
Revises: 0050
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0051"
down_revision = "0050"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "attendance_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("attendance_record_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("clock_in", sa.DateTime(timezone=False), nullable=False),
        sa.Column("clock_out", sa.DateTime(timezone=False), nullable=True),
        sa.Column("hours", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("source", sa.String(length=20), nullable=True, server_default=sa.text("'web'")),
        sa.Column("session_number", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
    )

    op.create_index("ix_att_sessions_tenant_id", "attendance_sessions", ["tenant_id"])
    op.create_index("ix_att_sessions_att_record_id", "attendance_sessions", ["attendance_record_id"])
    op.create_index("ix_att_sessions_employee_id", "attendance_sessions", ["employee_id"])
    op.create_index("idx_att_sessions_record_number", "attendance_sessions", ["attendance_record_id", "session_number"], unique=True)

    op.create_foreign_key("fk_att_sessions_tenant_id_tenants", "attendance_sessions", "tenants", ["tenant_id"], ["id"])
    op.create_foreign_key("fk_att_sessions_att_rec_id_recs", "attendance_sessions", "attendance_records", ["attendance_record_id"], ["id"])
    op.create_foreign_key("fk_att_sessions_employee_id_emps", "attendance_sessions", "employees", ["employee_id"], ["id"])

    op.execute("ALTER TABLE attendance_sessions ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE attendance_sessions FORCE ROW LEVEL SECURITY;")
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname='public' AND tablename='attendance_sessions' AND policyname='tenant_isolation_policy') THEN
                CREATE POLICY tenant_isolation_policy ON attendance_sessions USING (tenant_id = current_tenant_id());
            END IF;
        END; $$;
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON attendance_sessions;")
    op.execute("ALTER TABLE attendance_sessions DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_att_sessions_employee_id_emps", "attendance_sessions", type_="foreignkey")
    op.drop_constraint("fk_att_sessions_att_rec_id_recs", "attendance_sessions", type_="foreignkey")
    op.drop_constraint("fk_att_sessions_tenant_id_tenants", "attendance_sessions", type_="foreignkey")
    op.drop_index("idx_att_sessions_record_number", table_name="attendance_sessions")
    op.drop_index("ix_att_sessions_employee_id", table_name="attendance_sessions")
    op.drop_index("ix_att_sessions_att_record_id", table_name="attendance_sessions")
    op.drop_index("ix_att_sessions_tenant_id", table_name="attendance_sessions")
    op.drop_table("attendance_sessions")
