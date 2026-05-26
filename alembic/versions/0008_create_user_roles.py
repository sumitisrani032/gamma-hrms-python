"""create user roles table (Rails: 20260413060906_create_user_roles)

Revision ID: 0008
Revises: 0007
Create Date: 2026-05-25
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_roles",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index("ix_user_roles_tenant_id", "user_roles", ["tenant_id"], unique=False)
    op.create_index("ix_user_roles_user_id", "user_roles", ["user_id"], unique=False)
    op.create_index("ix_user_roles_role_id", "user_roles", ["role_id"], unique=False)
    op.create_index("uq_user_roles_user_id_role_id", "user_roles", ["user_id", "role_id"], unique=True)

    op.create_foreign_key(
        "fk_user_roles_tenant_id_tenants",
        "user_roles",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete=None,
    )
    
    op.create_foreign_key(
        "fk_user_roles_user_id_users",
        "user_roles",
        "users",
        ["user_id"],
        ["id"],
        ondelete=None,
    )
    
    op.create_foreign_key(
        "fk_user_roles_role_id_roles",
        "user_roles",
        "roles",
        ["role_id"],
        ["id"],
        ondelete=None,
    )

    # RLS policy for table `user_roles` using current_tenant_id()
    op.execute("ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE user_roles FORCE ROW LEVEL SECURITY;")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_policies
                WHERE schemaname = 'public'
                  AND tablename = 'user_roles'
                  AND policyname = 'tenant_isolation_policy'
            ) THEN
                CREATE POLICY tenant_isolation_policy
                ON user_roles
                USING (tenant_id = current_tenant_id());
            END IF;
        END;
        $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON user_roles;")
    op.execute("ALTER TABLE user_roles DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_user_roles_role_id_roles", "user_roles", type_="foreignkey")
    op.drop_constraint("fk_user_roles_user_id_users", "user_roles", type_="foreignkey")
    op.drop_constraint("fk_user_roles_tenant_id_tenants", "user_roles", type_="foreignkey")
    op.drop_index("uq_user_roles_user_id_role_id", table_name="user_roles")
    op.drop_index("ix_user_roles_role_id", table_name="user_roles")
    op.drop_index("ix_user_roles_user_id", table_name="user_roles")
    op.drop_index("ix_user_roles_tenant_id", table_name="user_roles")
    op.drop_table("user_roles")
