"""create locations table (Rails: 20260414070002_create_locations)

Revision ID: 0018
Revises: 0017
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0018"
down_revision = "0017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "locations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("state", sa.String(length=100), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=False, server_default=sa.text("'India'")),
        sa.Column("pincode", sa.String(length=20), nullable=True),
        sa.Column("timezone", sa.String(length=50), nullable=False, server_default=sa.text("'Asia/Kolkata'")),
        sa.Column("latitude", sa.Numeric(precision=10, scale=7), nullable=True),
        sa.Column("longitude", sa.Numeric(precision=10, scale=7), nullable=True),
        sa.Column("is_headquarters", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'active'")),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index("ix_locations_tenant_id", "locations", ["tenant_id"], unique=False)
    op.create_index("uq_locations_tenant_name", "locations", ["tenant_id", "name"], unique=True)

    op.create_foreign_key(
        "fk_locations_tenant_id_tenants",
        "locations",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete=None,
    )

    # RLS policy for table `locations` using current_tenant_id()
    op.execute("ALTER TABLE locations ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE locations FORCE ROW LEVEL SECURITY;")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_policies
                WHERE schemaname = 'public'
                  AND tablename = 'locations'
                  AND policyname = 'tenant_isolation_policy'
            ) THEN
                CREATE POLICY tenant_isolation_policy
                ON locations
                USING (tenant_id = current_tenant_id());
            END IF;
        END;
        $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON locations;")
    op.execute("ALTER TABLE locations DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_locations_tenant_id_tenants", "locations", type_="foreignkey")
    op.drop_index("uq_locations_tenant_name", table_name="locations")
    op.drop_index("ix_locations_tenant_id", table_name="locations")
    op.drop_table("locations")
