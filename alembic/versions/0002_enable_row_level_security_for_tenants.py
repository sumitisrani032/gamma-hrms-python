"""enable row level security for tenants

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-21
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


POLICY_NAME = "tenant_isolation_policy"


def upgrade() -> None:
    # Enable RLS on tenants table
    op.execute("ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;")

    # Ensure the tenant id function exists.
    # Assumes the application sets the current tenant id somewhere that
    # current_tenant_id() will resolve.
    # Use plain SQL (LANGUAGE sql) to avoid nested dollar-quoting issues
    op.execute(
        """
        CREATE OR REPLACE FUNCTION current_tenant_id()
        RETURNS uuid
        LANGUAGE sql
        STABLE
        AS $$
          SELECT NULLIF(current_setting('app.current_tenant_id', true), '')::uuid;
        $$;
        """
    )

    # Create the tenant isolation policy if missing
    op.execute(
        f"""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_policies
                WHERE schemaname = 'public'
                  AND tablename = 'tenants'
                  AND policyname = '{POLICY_NAME}'
            ) THEN
                CREATE POLICY {POLICY_NAME}
                ON tenants
                USING (id = current_tenant_id());
            END IF;
        END;
        $$;
        """
    )


def downgrade() -> None:
    op.execute(
        f"""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM pg_policies
                WHERE schemaname = 'public'
                  AND tablename = 'tenants'
                  AND policyname = '{POLICY_NAME}'
            ) THEN
                DROP POLICY {POLICY_NAME} ON tenants;
            END IF;
        END;
        $$;
        """
    )
