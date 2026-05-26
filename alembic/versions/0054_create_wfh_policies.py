"""create wfh policies table (Rails: 20260415120003_create_wfh_policies)

Revision ID: 0054
Revises: 0053
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0054"
down_revision = "0053"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "wfh_policies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("requires_approval", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("max_wfh_per_month", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("min_days_advance", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("allowed_on_probation", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("allowed_days", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("applicable_to", sa.String(length=20), nullable=False, server_default=sa.text("'all'")),
        sa.Column("applicable_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("priority", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
    )

    op.create_index("ix_wfh_policies_tenant_id", "wfh_policies", ["tenant_id"])
    op.create_index("idx_wfh_policies_unique", "wfh_policies", ["tenant_id", "name"], unique=True)
    op.create_index("idx_wfh_policies_tenant_active", "wfh_policies", ["tenant_id", "is_active"])

    op.create_foreign_key("fk_wfh_policies_tenant_id_tenants", "wfh_policies", "tenants", ["tenant_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint("fk_wfh_policies_tenant_id_tenants", "wfh_policies", type_="foreignkey")
    op.drop_index("idx_wfh_policies_tenant_active", table_name="wfh_policies")
    op.drop_index("idx_wfh_policies_unique", table_name="wfh_policies")
    op.drop_index("ix_wfh_policies_tenant_id", table_name="wfh_policies")
    op.drop_table("wfh_policies")
