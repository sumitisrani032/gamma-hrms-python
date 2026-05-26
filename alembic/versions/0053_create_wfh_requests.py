"""create wfh requests table (Rails: 20260415120002_create_wfh_requests)

Revision ID: 0053
Revises: 0052
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0053"
down_revision = "0052"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "wfh_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workflow_instance_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("approved_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("cancellation_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
    )

    op.create_index("ix_wfh_reqs_tenant_id", "wfh_requests", ["tenant_id"])
    op.create_index("ix_wfh_reqs_employee_id", "wfh_requests", ["employee_id"])
    op.create_index("ix_wfh_reqs_wf_instance_id", "wfh_requests", ["workflow_instance_id"])
    op.create_index("idx_wfh_requests_unique", "wfh_requests", ["tenant_id", "employee_id", "date"], unique=True)
    op.create_index("ix_wfh_reqs_status", "wfh_requests", ["status"])
    op.create_index("ix_wfh_reqs_date", "wfh_requests", ["date"])

    op.create_foreign_key("fk_wfh_reqs_tenant_id_tenants", "wfh_requests", "tenants", ["tenant_id"], ["id"])
    op.create_foreign_key("fk_wfh_reqs_employee_id_emps", "wfh_requests", "employees", ["employee_id"], ["id"])
    op.create_foreign_key("fk_wfh_reqs_wf_inst_id_wf_insts", "wfh_requests", "workflow_instances", ["workflow_instance_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint("fk_wfh_reqs_wf_inst_id_wf_insts", "wfh_requests", type_="foreignkey")
    op.drop_constraint("fk_wfh_reqs_employee_id_emps", "wfh_requests", type_="foreignkey")
    op.drop_constraint("fk_wfh_reqs_tenant_id_tenants", "wfh_requests", type_="foreignkey")
    op.drop_index("ix_wfh_reqs_date", table_name="wfh_requests")
    op.drop_index("ix_wfh_reqs_status", table_name="wfh_requests")
    op.drop_index("idx_wfh_requests_unique", table_name="wfh_requests")
    op.drop_index("ix_wfh_reqs_wf_instance_id", table_name="wfh_requests")
    op.drop_index("ix_wfh_reqs_employee_id", table_name="wfh_requests")
    op.drop_index("ix_wfh_reqs_tenant_id", table_name="wfh_requests")
    op.drop_table("wfh_requests")
