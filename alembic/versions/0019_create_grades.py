"""create grades table (Rails: 20260414070003_create_grades)

Revision ID: 0019
Revises: 0018
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0019"
down_revision = "0018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "grades",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=True),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'active'")),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index("ix_grades_tenant_id", "grades", ["tenant_id"], unique=False)
    op.create_index("uq_grades_tenant_name", "grades", ["tenant_id", "name"], unique=True)
    op.create_index("uq_grades_tenant_rank", "grades", ["tenant_id", "rank"], unique=True)

    op.create_foreign_key(
        "fk_grades_tenant_id_tenants",
        "grades",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete=None,
    )

    # RLS policy for table `grades` using current_tenant_id()
    op.execute("ALTER TABLE grades ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE grades FORCE ROW LEVEL SECURITY;")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_policies
                WHERE schemaname = 'public'
                  AND tablename = 'grades'
                  AND policyname = 'tenant_isolation_policy'
            ) THEN
                CREATE POLICY tenant_isolation_policy
                ON grades
                USING (tenant_id = current_tenant_id());
            END IF;
        END;
        $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON grades;")
    op.execute("ALTER TABLE grades DISABLE ROW LEVEL SECURITY;")
    op.drop_constraint("fk_grades_tenant_id_tenants", "grades", type_="foreignkey")
    op.drop_index("uq_grades_tenant_rank", table_name="grades")
    op.drop_index("uq_grades_tenant_name", table_name="grades")
    op.drop_index("ix_grades_tenant_id", table_name="grades")
    op.drop_table("grades")
