"""create payroll tables

Revision ID: 001
Revises:
Create Date: 2026-05-25 00:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --- salary_components ---
    op.create_table(
        "salary_components",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("tenant_location_id", postgresql.UUID(), nullable=False),
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_by", postgresql.UUID(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("calculation_type", sa.String(20), nullable=False),
        sa.Column("percentage_value", sa.Numeric(12, 2), nullable=True),
        sa.Column("percentage_of", sa.String(20), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
    )

    # --- employee_salaries ---
    op.create_table(
        "employee_salaries",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("employee_id", postgresql.UUID(), nullable=False),
        sa.Column("annual_ctc", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(20), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("created_by", postgresql.UUID(), nullable=False),
        sa.Column("approved_by", postgresql.UUID(), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
    )

    # --- employee_salary_components ---
    op.create_table(
        "employee_salary_components",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("employee_salary_id", sa.BigInteger(), nullable=False),
        sa.Column("salary_component_id", sa.BigInteger(), nullable=False),
        sa.Column("monthly_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
    )

    # --- employee_payslips ---
    op.create_table(
        "employee_payslips",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("employee_id", postgresql.UUID(), nullable=False),
        sa.Column("employee_salary_id", sa.BigInteger(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("component_snapshot", postgresql.JSONB(), nullable=False),
        sa.Column("gross_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("net_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("deduction_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("generated_on", sa.Date(), nullable=False),
        sa.Column("generated_by", postgresql.UUID(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column("total_attendance", sa.Integer(), nullable=False),
        sa.Column("paid_days", sa.Integer(), nullable=False),
        sa.Column("lop_days", sa.Integer(), nullable=True, server_default=sa.text("0")),
    )

    # --- Foreign keys ---
    op.create_foreign_key(
        "fk_employee_salaries_employee_id",
        "employee_salaries",
        "employees",
        ["employee_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_employee_salaries_created_by",
        "employee_salaries",
        "employees",
        ["created_by"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_employee_salaries_approved_by",
        "employee_salaries",
        "employees",
        ["approved_by"],
        ["id"],
    )
    # op.create_foreign_key(
    #     "fk_salary_components_tenant_location_id",
    #     "salary_components",
    #     "tenant_locations",
    #     ["tenant_location_id"],
    #     ["id"],
    # )
    op.create_foreign_key(
        "fk_salary_components_created_by",
        "salary_components",
        "employees",
        ["created_by"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_employee_salary_components_employee_salary_id",
        "employee_salary_components",
        "employee_salaries",
        ["employee_salary_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_employee_salary_components_salary_component_id",
        "employee_salary_components",
        "salary_components",
        ["salary_component_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_employee_payslips_employee_salary_id",
        "employee_payslips",
        "employee_salaries",
        ["employee_salary_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_employee_payslips_employee_id",
        "employee_payslips",
        "employees",
        ["employee_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_employee_payslips_generated_by",
        "employee_payslips",
        "employees",
        ["generated_by"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_employee_payslips_generated_by", "employee_payslips", type_="foreignkey")
    op.drop_constraint("fk_employee_payslips_employee_id", "employee_payslips", type_="foreignkey")
    op.drop_constraint("fk_employee_payslips_employee_salary_id", "employee_payslips", type_="foreignkey")
    op.drop_constraint("fk_employee_salary_components_salary_component_id", "employee_salary_components", type_="foreignkey")
    op.drop_constraint("fk_employee_salary_components_employee_salary_id", "employee_salary_components", type_="foreignkey")
    op.drop_constraint("fk_salary_components_created_by", "salary_components", type_="foreignkey")
    op.drop_constraint("fk_salary_components_tenant_location_id", "salary_components", type_="foreignkey")
    op.drop_constraint("fk_employee_salaries_approved_by", "employee_salaries", type_="foreignkey")
    op.drop_constraint("fk_employee_salaries_created_by", "employee_salaries", type_="foreignkey")
    op.drop_constraint("fk_employee_salaries_employee_id", "employee_salaries", type_="foreignkey")
    op.drop_table("employee_payslips")
    op.drop_table("employee_salary_components")
    op.drop_table("employee_salaries")
    op.drop_table("salary_components")
