"""create holiday calendars table (Rails: 20260414070019_create_holiday_calendars)

Revision ID: 0035
Revises: 0034
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0035"
down_revision = "0034"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "holiday_calendars",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("location_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index("ix_hol_cals_tenant_id", "holiday_calendars", ["tenant_id"], unique=False)
    op.create_index("ix_hol_cals_location_id", "holiday_calendars", ["location_id"], unique=False)
    op.create_index("idx_holiday_calendars_unique", "holiday_calendars", ["tenant_id", "location_id", "year"], unique=True)

    op.create_foreign_key(
        "fk_hol_cals_tenant_id_tenants",
        "holiday_calendars",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete=None,
    )
    op.create_foreign_key(
        "fk_hol_cals_location_id_locs",
        "holiday_calendars",
        "locations",
        ["location_id"],
        ["id"],
        ondelete=None,
    )

    # RLS policy for table `holiday_calendars` using current_tenant_id()
    op.execute("ALTER TABLE holiday_calendars ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE holiday_calendars FORCE ROW LEVEL SECURITY;")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_policies
                WHERE schemaname = 'public'
                  AND tablename = 'holiday_calendars'
                  AND policyname = 'tenant_isolation_policy'
            ) THEN
                CREATE POLICY tenant_isolation_policy
                ON holiday_calendars
                USING (tenant_id = current_tenant_id());
            END IF;
        END;
        $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON holiday_calendars;")
    op.execute("ALTER TABLE holiday_calendars DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_hol_cals_location_id_locs", "holiday_calendars", type_="foreignkey")
    op.drop_constraint("fk_hol_cals_tenant_id_tenants", "holiday_calendars", type_="foreignkey")
    op.drop_index("idx_holiday_calendars_unique", table_name="holiday_calendars")
    op.drop_index("ix_hol_cals_location_id", table_name="holiday_calendars")
    op.drop_index("ix_hol_cals_tenant_id", table_name="holiday_calendars")
    op.drop_table("holiday_calendars")
