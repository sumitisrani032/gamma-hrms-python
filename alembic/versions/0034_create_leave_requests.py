"""create leave requests table (Rails: 20260414070018_create_leave_requests)

Revision ID: 0034
Revises: 0033
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0034"
down_revision = "0033"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "leave_requests",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("leave_type_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("start_half", sa.String(length=15), nullable=True),
        sa.Column("end_half", sa.String(length=15), nullable=True),
        sa.Column("number_of_days", sa.Numeric(precision=5, scale=1), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("workflow_instance_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("cancellation_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index("ix_leave_reqs_tenant_id", "leave_requests", ["tenant_id"], unique=False)
    op.create_index("ix_leave_reqs_employee_id", "leave_requests", ["employee_id"], unique=False)
    op.create_index("ix_leave_reqs_leave_type_id", "leave_requests", ["leave_type_id"], unique=False)
    op.create_index("ix_leave_reqs_status", "leave_requests", ["status"], unique=False)
    op.create_index("idx_leave_requests_dates", "leave_requests", ["start_date", "end_date"], unique=False)

    op.create_foreign_key(
        "fk_leave_reqs_tenant_id_tenants",
        "leave_requests",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete=None,
    )
    op.create_foreign_key(
        "fk_leave_reqs_employee_id_emps",
        "leave_requests",
        "employees",
        ["employee_id"],
        ["id"],
        ondelete=None,
    )
    op.create_foreign_key(
        "fk_leave_reqs_leave_type_id_lt",
        "leave_requests",
        "leave_types",
        ["leave_type_id"],
        ["id"],
        ondelete=None,
    )
    op.create_foreign_key(
        "fk_leave_reqs_wf_inst_id_wf_insts",
        "leave_requests",
        "workflow_instances",
        ["workflow_instance_id"],
        ["id"],
        ondelete=None,
    )
    op.create_foreign_key(
        "fk_leave_reqs_approved_by_id_users",
        "leave_requests",
        "users",
        ["approved_by_id"],
        ["id"],
        ondelete=None,
    )

    # RLS policy for table `leave_requests` using current_tenant_id()
    op.execute("ALTER TABLE leave_requests ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE leave_requests FORCE ROW LEVEL SECURITY;")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_policies
                WHERE schemaname = 'public'
                  AND tablename = 'leave_requests'
                  AND policyname = 'tenant_isolation_policy'
            ) THEN
                CREATE POLICY tenant_isolation_policy
                ON leave_requests
                USING (tenant_id = current_tenant_id());
            END IF;
        END;
        $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON leave_requests;")
    op.execute("ALTER TABLE leave_requests DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_leave_reqs_approved_by_id_users", "leave_requests", type_="foreignkey")
    op.drop_constraint("fk_leave_reqs_wf_inst_id_wf_insts", "leave_requests", type_="foreignkey")
    op.drop_constraint("fk_leave_reqs_leave_type_id_lt", "leave_requests", type_="foreignkey")
    op.drop_constraint("fk_leave_reqs_employee_id_emps", "leave_requests", type_="foreignkey")
    op.drop_constraint("fk_leave_reqs_tenant_id_tenants", "leave_requests", type_="foreignkey")
    op.drop_index("idx_leave_requests_dates", table_name="leave_requests")
    op.drop_index("ix_leave_reqs_status", table_name="leave_requests")
    op.drop_index("ix_leave_reqs_leave_type_id", table_name="leave_requests")
    op.drop_index("ix_leave_reqs_employee_id", table_name="leave_requests")
    op.drop_index("ix_leave_reqs_tenant_id", table_name="leave_requests")
    op.drop_table("leave_requests")
