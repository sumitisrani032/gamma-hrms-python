"""create role permissions table (Rails: 20260413060905_create_role_permissions)

Revision ID: 0007
Revises: 0006
Create Date: 2026-05-25
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "role_permissions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("permission_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index("ix_role_permissions_role_id", "role_permissions", ["role_id"], unique=False)
    op.create_index("ix_role_permissions_permission_id", "role_permissions", ["permission_id"], unique=False)
    op.create_index("uq_role_permissions_role_id_permission_id", "role_permissions", ["role_id", "permission_id"], unique=True)

    op.create_foreign_key(
        "fk_role_permissions_role_id_roles",
        "role_permissions",
        "roles",
        ["role_id"],
        ["id"],
        ondelete=None,
    )
    
    op.create_foreign_key(
        "fk_role_permissions_permission_id_permissions",
        "role_permissions",
        "permissions",
        ["permission_id"],
        ["id"],
        ondelete=None,
    )


def downgrade() -> None:
    op.drop_constraint("fk_role_permissions_permission_id_permissions", "role_permissions", type_="foreignkey")
    op.drop_constraint("fk_role_permissions_role_id_roles", "role_permissions", type_="foreignkey")
    op.drop_index("uq_role_permissions_role_id_permission_id", table_name="role_permissions")
    op.drop_index("ix_role_permissions_permission_id", table_name="role_permissions")
    op.drop_index("ix_role_permissions_role_id", table_name="role_permissions")
    op.drop_table("role_permissions")
