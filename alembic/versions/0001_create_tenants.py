"""create_tenants

Revision ID: 0001
Revises:
Create Date: 2026-05-21
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0001"
down_revision = "0000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "subdomain",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "domain",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "logo_url",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default=sa.text("'trial'"),
        ),
        sa.Column(
            "plan",
            sa.String(length=50),
            nullable=False,
            server_default=sa.text("'starter'"),
        ),
        sa.Column(
            "settings",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # Unique subdomain index
    op.create_index(
        "ix_tenants_subdomain",
        "tenants",
        ["subdomain"],
        unique=True,
    )

    # Partial unique index for domain
    op.create_index(
        "uq_tenants_domain_not_null",
        "tenants",
        ["domain"],
        unique=True,
        postgresql_where=sa.text("domain IS NOT NULL"),
    )

    # Status index
    op.create_index(
        "ix_tenants_status",
        "tenants",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_tenants_status", table_name="tenants")
    op.drop_index("uq_tenants_domain_not_null", table_name="tenants")
    op.drop_index("ix_tenants_subdomain", table_name="tenants")

    op.drop_table("tenants")

    # Optional: remove extension
    op.execute('DROP EXTENSION IF EXISTS "pgcrypto";')
