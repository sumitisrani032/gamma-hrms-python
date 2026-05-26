"""create shift assignments table (Rails: 20260414070022_create_shift_assignments)

Revision ID: 0038
Revises: 0037
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0038"
down_revision = "0037"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "shift_assignments",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("shift_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("assigned_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index("ix_shift_assignments_tenant_id", "shift_assignments", ["tenant_id"], unique=False)
    op.create_index("ix_shift_assignments_employee_id", "shift_assignments", ["employee_id"], unique=False)
    op.create_index("ix_shift_assignments_shift_id", "shift_assignments", ["shift_id"], unique=False)
    op.create_index("idx_shift_assignments_unique", "shift_assignments", ["tenant_id", "employee_id", "effective_from"], unique=False)

    op.create_foreign_key(
        "fk_shift_assignments_tenant_id_tenants",
        "shift_assignments",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete=None,
    )
    op.create_foreign_key(
        "fk_shift_assignments_employee_id_emps",
        "shift_assignments",
        "employees",
        ["employee_id"],
        ["id"],
        ondelete=None,
    )
    op.create_foreign_key(
        "fk_shift_assignments_shift_id_shifts",
        "shift_assignments",
        "shifts",
        ["shift_id"],
        ["id"],
        ondelete=None,
    )
    op.create_foreign_key(
        "fk_shift_assignments_assigned_by_id_users",
        "shift_assignments",
        "users",
        ["assigned_by_id"],
        ["id"],
        ondelete=None,
    )

    # RLS policy for table `shift_assignments` using current_tenant_id()
    op.execute("ALTER TABLE shift_assignments ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE shift_assignments FORCE ROW LEVEL SECURITY;")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_policies
                WHERE schemaname = 'public'
                  AND tablename = 'shift_assignments'
                  AND policyname = 'tenant_isolation_policy'
            ) THEN
                CREATE POLICY tenant_isolation_policy
                ON shift_assignments
                USING (tenant_id = current_tenant_id());
            END IF;
        END;
        $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON shift_assignments;")
    op.execute("ALTER TABLE shift_assignments DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_shift_assignments_assigned_by_id_users", "shift_assignments", type_="foreignkey")
    op.drop_constraint("fk_shift_assignments_shift_id_shifts", "shift_assignments", type_="foreignkey")
    op.drop_constraint("fk_shift_assignments_employee_id_emps", "shift_assignments", type_="foreignkey")
    op.drop_constraint("fk_shift_assignments_tenant_id_tenants", "shift_assignments", type_="foreignkey")
    op.drop_index("idx_shift_assignments_unique", table_name="shift_assignments")
    op.drop_index("ix_shift_assignments_shift_id", table_name="shift_assignments")
    op.drop_index("ix_shift_assignments_employee_id", table_name="shift_assignments")
    op.drop_index("ix_shift_assignments_tenant_id", table_name="shift_assignments")
    op.drop_table("shift_assignments")
