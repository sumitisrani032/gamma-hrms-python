"""make wfh uniqueness partial (Rails: 20260420140001_make_wfh_uniqueness_partial)

Revision ID: 0059
Revises: 0058
Create Date: 2026-05-26

The original unique index on (tenant_id, employee_id, date) blocked re-applying
for a date after a WFH request was cancelled or rejected. This migration replaces
it with a partial index that only enforces uniqueness for active statuses
(pending / approved).
"""

from alembic import op
import sqlalchemy as sa

revision = "0059"
down_revision = "0058"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("idx_wfh_requests_unique", table_name="wfh_requests")
    op.create_index(
        "idx_wfh_requests_active_unique",
        "wfh_requests",
        ["tenant_id", "employee_id", "date"],
        unique=True,
        postgresql_where=sa.text("status IN ('pending', 'approved')"),
    )


def downgrade() -> None:
    op.drop_index("idx_wfh_requests_active_unique", table_name="wfh_requests")
    op.create_index(
        "idx_wfh_requests_unique",
        "wfh_requests",
        ["tenant_id", "employee_id", "date"],
        unique=True,
    )
