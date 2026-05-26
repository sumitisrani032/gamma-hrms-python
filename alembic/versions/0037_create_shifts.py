"""create shifts table (Rails: 20260414070021_create_shifts)

Revision ID: 0037
Revises: 0036
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0037"
down_revision = "0036"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "shifts",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=True),
        sa.Column("start_time", sa.Time(timezone=False), nullable=False),
        sa.Column("end_time", sa.Time(timezone=False), nullable=False),
        sa.Column("grace_minutes", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("half_day_hours", sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column("full_day_hours", sa.Numeric(precision=4, scale=2), nullable=False),
        sa.Column("is_night_shift", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("weekly_offs", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[\"saturday\", \"sunday\"]'::jsonb")),
        sa.Column("is_flexible", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("min_hours", sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index("ix_shifts_tenant_id", "shifts", ["tenant_id"], unique=False)
    op.create_index("idx_shifts_unique", "shifts", ["tenant_id", "name"], unique=True)

    op.create_foreign_key(
        "fk_shifts_tenant_id_tenants",
        "shifts",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete=None,
    )

    # RLS policy for table `shifts` using current_tenant_id()
    op.execute("ALTER TABLE shifts ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE shifts FORCE ROW LEVEL SECURITY;")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_policies
                WHERE schemaname = 'public'
                  AND tablename = 'shifts'
                  AND policyname = 'tenant_isolation_policy'
            ) THEN
                CREATE POLICY tenant_isolation_policy
                ON shifts
                USING (tenant_id = current_tenant_id());
            END IF;
        END;
        $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON shifts;")
    op.execute("ALTER TABLE shifts DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_shifts_tenant_id_tenants", "shifts", type_="foreignkey")
    op.drop_index("idx_shifts_unique", table_name="shifts")
    op.drop_index("ix_shifts_tenant_id", table_name="shifts")
    op.drop_table("shifts")
