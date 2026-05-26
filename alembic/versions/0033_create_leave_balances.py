"""create leave balances table (Rails: 20260414070017_create_leave_balances)

Revision ID: 0033
Revises: 0032
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0033"
down_revision = "0032"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "leave_balances",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("leave_type_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("entitled", sa.Numeric(precision=5, scale=1), nullable=False, server_default=sa.text("0")),
        sa.Column("accrued", sa.Numeric(precision=5, scale=1), nullable=False, server_default=sa.text("0")),
        sa.Column("used", sa.Numeric(precision=5, scale=1), nullable=False, server_default=sa.text("0")),
        sa.Column("carry_forwarded", sa.Numeric(precision=5, scale=1), nullable=False, server_default=sa.text("0")),
        sa.Column("adjusted", sa.Numeric(precision=5, scale=1), nullable=False, server_default=sa.text("0")),
        sa.Column("balance", sa.Numeric(precision=5, scale=1), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index("ix_leave_balances_tenant_id", "leave_balances", ["tenant_id"], unique=False)
    op.create_index("ix_leave_balances_employee_id", "leave_balances", ["employee_id"], unique=False)
    op.create_index("ix_leave_balances_leave_type_id", "leave_balances", ["leave_type_id"], unique=False)
    op.create_index("idx_leave_balances_unique", "leave_balances", ["tenant_id", "employee_id", "leave_type_id", "year"], unique=True)

    op.create_foreign_key(
        "fk_leave_balances_tenant_id_tenants",
        "leave_balances",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete=None,
    )
    op.create_foreign_key(
        "fk_leave_balances_employee_id_emps",
        "leave_balances",
        "employees",
        ["employee_id"],
        ["id"],
        ondelete=None,
    )
    op.create_foreign_key(
        "fk_leave_balances_leave_type_id_lt",
        "leave_balances",
        "leave_types",
        ["leave_type_id"],
        ["id"],
        ondelete=None,
    )

    # RLS policy for table `leave_balances` using current_tenant_id()
    op.execute("ALTER TABLE leave_balances ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE leave_balances FORCE ROW LEVEL SECURITY;")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_policies
                WHERE schemaname = 'public'
                  AND tablename = 'leave_balances'
                  AND policyname = 'tenant_isolation_policy'
            ) THEN
                CREATE POLICY tenant_isolation_policy
                ON leave_balances
                USING (tenant_id = current_tenant_id());
            END IF;
        END;
        $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON leave_balances;")
    op.execute("ALTER TABLE leave_balances DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_leave_balances_leave_type_id_lt", "leave_balances", type_="foreignkey")
    op.drop_constraint("fk_leave_balances_employee_id_emps", "leave_balances", type_="foreignkey")
    op.drop_constraint("fk_leave_balances_tenant_id_tenants", "leave_balances", type_="foreignkey")
    op.drop_index("idx_leave_balances_unique", table_name="leave_balances")
    op.drop_index("ix_leave_balances_leave_type_id", table_name="leave_balances")
    op.drop_index("ix_leave_balances_employee_id", table_name="leave_balances")
    op.drop_index("ix_leave_balances_tenant_id", table_name="leave_balances")
    op.drop_table("leave_balances")
