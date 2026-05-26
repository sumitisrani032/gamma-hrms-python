"""add setup tracking to tenants (Rails: 20260414080001_add_setup_tracking_to_tenants)

Revision ID: 0045
Revises: 0044
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0045"
down_revision = "0044"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tenants", sa.Column("setup_completed_at", sa.DateTime(timezone=False), nullable=True))
    op.add_column("tenants", sa.Column("setup_steps", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")))


def downgrade() -> None:
    op.drop_column("tenants", "setup_steps")
    op.drop_column("tenants", "setup_completed_at")
