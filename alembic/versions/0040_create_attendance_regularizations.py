"""create attendance regularizations table (Rails: 20260414070024_create_attendance_regularizations)

Revision ID: 0040
Revises: 0039
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0040"
down_revision = "0039"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "attendance_regularizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("attendance_record_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("original_clock_in", sa.DateTime(timezone=False), nullable=True),
        sa.Column("original_clock_out", sa.DateTime(timezone=False), nullable=True),
        sa.Column("requested_clock_in", sa.DateTime(timezone=False), nullable=False),
        sa.Column("requested_clock_out", sa.DateTime(timezone=False), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("workflow_instance_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
    )

    op.create_index("ix_att_regs_tenant_id", "attendance_regularizations", ["tenant_id"])
    op.create_index("ix_att_regs_employee_id", "attendance_regularizations", ["employee_id"])
    op.create_index("ix_att_regs_att_record_id", "attendance_regularizations", ["attendance_record_id"])
    op.create_index("ix_att_regs_status", "attendance_regularizations", ["status"])

    op.create_foreign_key("fk_att_regs_tenant_id_tenants", "attendance_regularizations", "tenants", ["tenant_id"], ["id"])
    op.create_foreign_key("fk_att_regs_employee_id_emps", "attendance_regularizations", "employees", ["employee_id"], ["id"])
    op.create_foreign_key("fk_att_regs_att_rec_id_att_recs", "attendance_regularizations", "attendance_records", ["attendance_record_id"], ["id"])
    op.create_foreign_key("fk_att_regs_wf_inst_id_wf_insts", "attendance_regularizations", "workflow_instances", ["workflow_instance_id"], ["id"])
    op.create_foreign_key("fk_att_regs_appr_by_id_users", "attendance_regularizations", "users", ["approved_by_id"], ["id"])

    op.execute("ALTER TABLE attendance_regularizations ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE attendance_regularizations FORCE ROW LEVEL SECURITY;")
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname='public' AND tablename='attendance_regularizations' AND policyname='tenant_isolation_policy') THEN
                CREATE POLICY tenant_isolation_policy ON attendance_regularizations USING (tenant_id = current_tenant_id());
            END IF;
        END; $$;
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON attendance_regularizations;")
    op.execute("ALTER TABLE attendance_regularizations DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_att_regs_appr_by_id_users", "attendance_regularizations", type_="foreignkey")
    op.drop_constraint("fk_att_regs_wf_inst_id_wf_insts", "attendance_regularizations", type_="foreignkey")
    op.drop_constraint("fk_att_regs_att_rec_id_att_recs", "attendance_regularizations", type_="foreignkey")
    op.drop_constraint("fk_att_regs_employee_id_emps", "attendance_regularizations", type_="foreignkey")
    op.drop_constraint("fk_att_regs_tenant_id_tenants", "attendance_regularizations", type_="foreignkey")
    op.drop_index("ix_att_regs_status", table_name="attendance_regularizations")
    op.drop_index("ix_att_regs_att_record_id", table_name="attendance_regularizations")
    op.drop_index("ix_att_regs_employee_id", table_name="attendance_regularizations")
    op.drop_index("ix_att_regs_tenant_id", table_name="attendance_regularizations")
    op.drop_table("attendance_regularizations")
