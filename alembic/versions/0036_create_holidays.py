"""create holidays table (Rails: 20260414070020_create_holidays)

Revision ID: 0036
Revises: 0035
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0036"
down_revision = "0035"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "holidays",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("holiday_calendar_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("holiday_type", sa.String(length=20), nullable=False, server_default=sa.text("'mandatory'")),
        sa.Column("is_half_day", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index("ix_holidays_tenant_id", "holidays", ["tenant_id"], unique=False)
    op.create_index("ix_holidays_holiday_calendar_id", "holidays", ["holiday_calendar_id"], unique=False)
    op.create_index("idx_holidays_unique", "holidays", ["tenant_id", "holiday_calendar_id", "date"], unique=True)

    op.create_foreign_key(
        "fk_holidays_tenant_id_tenants",
        "holidays",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete=None,
    )
    op.create_foreign_key(
        "fk_holidays_hol_cal_id_hol_cals",
        "holidays",
        "holiday_calendars",
        ["holiday_calendar_id"],
        ["id"],
        ondelete=None,
    )

    # RLS policy for table `holidays` using current_tenant_id()
    op.execute("ALTER TABLE holidays ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE holidays FORCE ROW LEVEL SECURITY;")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_policies
                WHERE schemaname = 'public'
                  AND tablename = 'holidays'
                  AND policyname = 'tenant_isolation_policy'
            ) THEN
                CREATE POLICY tenant_isolation_policy
                ON holidays
                USING (tenant_id = current_tenant_id());
            END IF;
        END;
        $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON holidays;")
    op.execute("ALTER TABLE holidays DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_holidays_hol_cal_id_hol_cals", "holidays", type_="foreignkey")
    op.drop_constraint("fk_holidays_tenant_id_tenants", "holidays", type_="foreignkey")
    op.drop_index("idx_holidays_unique", table_name="holidays")
    op.drop_index("ix_holidays_holiday_calendar_id", table_name="holidays")
    op.drop_index("ix_holidays_tenant_id", table_name="holidays")
    op.drop_table("holidays")
