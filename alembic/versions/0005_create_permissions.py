"""create permissions table (Rails: 20260413060902_create_permissions)

Revision ID: 0005
Revises: 0004
Create Date: 2026-05-21
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "permissions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("resource", sa.String(length=100), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("scope", sa.String(length=20), nullable=False, server_default=sa.text("'self'")),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index(
        "uq_permissions_resource_action_scope",
        "permissions",
        ["resource", "action", "scope"],
        unique=True,
    )
    op.create_index("ix_permissions_resource", "permissions", ["resource"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_permissions_resource", table_name="permissions")
    op.drop_index("uq_permissions_resource_action_scope", table_name="permissions")
    op.drop_table("permissions")

