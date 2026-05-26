"""add wfh policy to wfh requests (Rails: 20260415120004_add_wfh_policy_to_wfh_requests)

Revision ID: 0055
Revises: 0054
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0055"
down_revision = "0054"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("wfh_requests", sa.Column("wfh_policy_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index("ix_wfh_reqs_wfh_policy_id", "wfh_requests", ["wfh_policy_id"])
    op.create_foreign_key("fk_wfh_reqs_wfh_policy_id_pols", "wfh_requests", "wfh_policies", ["wfh_policy_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint("fk_wfh_reqs_wfh_policy_id_pols", "wfh_requests", type_="foreignkey")
    op.drop_index("ix_wfh_reqs_wfh_policy_id", table_name="wfh_requests")
    op.drop_column("wfh_requests", "wfh_policy_id")
