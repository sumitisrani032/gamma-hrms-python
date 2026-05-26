"""create leave policies table (Rails: 20260414070016_create_leave_policies)

Revision ID: 0032
Revises: 0031
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0032"
down_revision = "0031"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "leave_policies",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("leave_type_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("accrual_type", sa.String(length=20), nullable=False, server_default=sa.text("'annual'")),
        sa.Column("annual_quota", sa.Numeric(precision=5, scale=1), nullable=False),
        sa.Column("monthly_accrual", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("prorate_on_joining", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("prorate_on_exit", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("proration_basis", sa.String(length=20), nullable=True, server_default=sa.text("'calendar_days'")),
        sa.Column("applicable_to", sa.String(length=20), nullable=False, server_default=sa.text("'all'")),
        sa.Column("applicable_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("min_days_per_request", sa.Numeric(precision=3, scale=1), nullable=True),
        sa.Column("max_days_per_request", sa.Numeric(precision=5, scale=1), nullable=True),
        sa.Column("requires_approval", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("advance_days_required", sa.Integer(), nullable=True, server_default=sa.text("0")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index("ix_leave_policies_tenant_id", "leave_policies", ["tenant_id"], unique=False)
    op.create_index("ix_leave_policies_leave_type_id", "leave_policies", ["leave_type_id"], unique=False)
    op.create_index("idx_leave_policies_unique", "leave_policies", ["tenant_id", "leave_type_id", "name"], unique=True)

    op.create_foreign_key(
        "fk_leave_policies_tenant_id_tenants",
        "leave_policies",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete=None,
    )
    op.create_foreign_key(
        "fk_leave_policies_leave_type_id_lt",
        "leave_policies",
        "leave_types",
        ["leave_type_id"],
        ["id"],
        ondelete=None,
    )

    # RLS policy for table `leave_policies` using current_tenant_id()
    op.execute("ALTER TABLE leave_policies ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE leave_policies FORCE ROW LEVEL SECURITY;")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_policies
                WHERE schemaname = 'public'
                  AND tablename = 'leave_policies'
                  AND policyname = 'tenant_isolation_policy'
            ) THEN
                CREATE POLICY tenant_isolation_policy
                ON leave_policies
                USING (tenant_id = current_tenant_id());
            END IF;
        END;
        $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON leave_policies;")
    op.execute("ALTER TABLE leave_policies DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_leave_policies_leave_type_id_lt", "leave_policies", type_="foreignkey")
    op.drop_constraint("fk_leave_policies_tenant_id_tenants", "leave_policies", type_="foreignkey")
    op.drop_index("idx_leave_policies_unique", table_name="leave_policies")
    op.drop_index("ix_leave_policies_leave_type_id", table_name="leave_policies")
    op.drop_index("ix_leave_policies_tenant_id", table_name="leave_policies")
    op.drop_table("leave_policies")
