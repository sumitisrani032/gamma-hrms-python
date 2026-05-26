"""add head employee fk to departments (Rails: 20260414070008_add_head_employee_fk_to_departments)

Revision ID: 0024
Revises: 0023
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0024"
down_revision = "0023"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_foreign_key(
        "fk_depts_head_emp_id_emps",
        "departments",
        "employees",
        ["head_employee_id"],
        ["id"],
        ondelete=None,
    )
    op.create_foreign_key(
        "fk_bus_units_head_emp_id_emps",
        "business_units",
        "employees",
        ["head_employee_id"],
        ["id"],
        ondelete=None,
    )


def downgrade() -> None:
    op.drop_constraint("fk_bus_units_head_emp_id_emps", "business_units", type_="foreignkey")
    op.drop_constraint("fk_depts_head_emp_id_emps", "departments", type_="foreignkey")
