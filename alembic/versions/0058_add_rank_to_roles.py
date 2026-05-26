"""add rank to roles (Rails: 20260420130001_add_rank_to_roles)

Revision ID: 0058
Revises: 0057
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa

revision = "0058"
down_revision = "0057"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("roles", sa.Column("rank", sa.Integer(), nullable=False, server_default=sa.text("0")))
    op.create_index("ix_roles_tenant_id_rank", "roles", ["tenant_id", "rank"])


def downgrade() -> None:
    op.drop_index("ix_roles_tenant_id_rank", table_name="roles")
    op.drop_column("roles", "rank")
