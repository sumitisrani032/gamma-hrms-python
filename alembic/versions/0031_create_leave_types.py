"""create leave types table (Rails: 20260414070015_create_leave_types)

Revision ID: 0031
Revises: 0030
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0031"
down_revision = "0030"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "leave_types",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_paid", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_carry_forward", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("max_carry_forward_days", sa.Numeric(precision=5, scale=1), nullable=True, server_default=sa.text("0")),
        sa.Column("is_encashable", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("max_encashment_days", sa.Numeric(precision=5, scale=1), nullable=True, server_default=sa.text("0")),
        sa.Column("is_half_day_allowed", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_negative_balance_allowed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("max_negative_days", sa.Numeric(precision=5, scale=1), nullable=True, server_default=sa.text("0")),
        sa.Column("requires_attachment", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("min_days_before_application", sa.Integer(), nullable=True, server_default=sa.text("0")),
        sa.Column("max_consecutive_days", sa.Integer(), nullable=True),
        sa.Column("gender_applicable", sa.String(length=20), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("color_code", sa.String(length=10), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index("ix_leave_types_tenant_id", "leave_types", ["tenant_id"], unique=False)
    op.create_index("idx_leave_types_tenant_code", "leave_types", ["tenant_id", "code"], unique=True)
    op.create_index("idx_leave_types_tenant_name", "leave_types", ["tenant_id", "name"], unique=True)

    op.create_foreign_key(
        "fk_leave_types_tenant_id_tenants",
        "leave_types",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete=None,
    )

    # RLS policy for table `leave_types` using current_tenant_id()
    op.execute("ALTER TABLE leave_types ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE leave_types FORCE ROW LEVEL SECURITY;")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_policies
                WHERE schemaname = 'public'
                  AND tablename = 'leave_types'
                  AND policyname = 'tenant_isolation_policy'
            ) THEN
                CREATE POLICY tenant_isolation_policy
                ON leave_types
                USING (tenant_id = current_tenant_id());
            END IF;
        END;
        $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON leave_types;")
    op.execute("ALTER TABLE leave_types DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_leave_types_tenant_id_tenants", "leave_types", type_="foreignkey")
    op.drop_index("idx_leave_types_tenant_name", table_name="leave_types")
    op.drop_index("idx_leave_types_tenant_code", table_name="leave_types")
    op.drop_index("ix_leave_types_tenant_id", table_name="leave_types")
    op.drop_table("leave_types")
