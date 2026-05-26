"""remove role from users (Rails: 20260413065433_remove_role_from_users)

Revision ID: 0009
Revises: 0008
Create Date: 2026-05-25
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("users", "role")


def downgrade() -> None:
    op.add_column("users", sa.Column("role", sa.String(length=50), nullable=False, server_default=sa.text("'employee'")))
