"""create employee lifecycle events table (Rails: 20260414070012_create_employee_lifecycle_events)

Revision ID: 0028
Revises: 0027
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0028"
down_revision = "0027"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "employee_lifecycle_events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("effective_date", sa.Date(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("previous_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("new_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("performed_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("workflow_instance_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index("ix_emp_lifecycle_events_tenant_id", "employee_lifecycle_events", ["tenant_id"], unique=False)
    op.create_index("ix_emp_lifecycle_events_employee_id", "employee_lifecycle_events", ["employee_id"], unique=False)
    op.create_index("ix_emp_lifecycle_events_event_type", "employee_lifecycle_events", ["event_type"], unique=False)
    op.create_index("ix_emp_lifecycle_events_event_date", "employee_lifecycle_events", ["event_date"], unique=False)

    op.create_foreign_key(
        "fk_emp_lc_ev_tenant_id_tenants",
        "employee_lifecycle_events",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete=None,
    )
    op.create_foreign_key(
        "fk_emp_lc_ev_employee_id_emps",
        "employee_lifecycle_events",
        "employees",
        ["employee_id"],
        ["id"],
        ondelete=None,
    )
    op.create_foreign_key(
        "fk_emp_lc_ev_perf_by_id_users",
        "employee_lifecycle_events",
        "users",
        ["performed_by_id"],
        ["id"],
        ondelete=None,
    )
    op.create_foreign_key(
        "fk_emp_lc_ev_wf_inst_id_wf_insts",
        "employee_lifecycle_events",
        "workflow_instances",
        ["workflow_instance_id"],
        ["id"],
        ondelete=None,
    )

    # RLS policy for table `employee_lifecycle_events` using current_tenant_id()
    op.execute("ALTER TABLE employee_lifecycle_events ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE employee_lifecycle_events FORCE ROW LEVEL SECURITY;")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_policies
                WHERE schemaname = 'public'
                  AND tablename = 'employee_lifecycle_events'
                  AND policyname = 'tenant_isolation_policy'
            ) THEN
                CREATE POLICY tenant_isolation_policy
                ON employee_lifecycle_events
                USING (tenant_id = current_tenant_id());
            END IF;
        END;
        $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON employee_lifecycle_events;")
    op.execute("ALTER TABLE employee_lifecycle_events DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_emp_lc_ev_wf_inst_id_wf_insts", "employee_lifecycle_events", type_="foreignkey")
    op.drop_constraint("fk_emp_lc_ev_perf_by_id_users", "employee_lifecycle_events", type_="foreignkey")
    op.drop_constraint("fk_emp_lc_ev_employee_id_emps", "employee_lifecycle_events", type_="foreignkey")
    op.drop_constraint("fk_emp_lc_ev_tenant_id_tenants", "employee_lifecycle_events", type_="foreignkey")
    op.drop_index("ix_emp_lifecycle_events_event_date", table_name="employee_lifecycle_events")
    op.drop_index("ix_emp_lifecycle_events_event_type", table_name="employee_lifecycle_events")
    op.drop_index("ix_emp_lifecycle_events_employee_id", table_name="employee_lifecycle_events")
    op.drop_index("ix_emp_lifecycle_events_tenant_id", table_name="employee_lifecycle_events")
    op.drop_table("employee_lifecycle_events")
