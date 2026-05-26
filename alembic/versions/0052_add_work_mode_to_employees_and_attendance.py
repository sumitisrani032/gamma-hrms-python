"""add work mode to employees and attendance (Rails: 20260415120001_add_work_mode_to_employees_and_attendance)

Revision ID: 0052
Revises: 0051
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa

revision = "0052"
down_revision = "0051"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("employees", sa.Column("work_mode", sa.String(length=20), nullable=False, server_default=sa.text("'office'")))
    op.add_column("attendance_records", sa.Column("work_mode", sa.String(length=20), nullable=False, server_default=sa.text("'office'")))
    op.create_index("ix_employees_work_mode", "employees", ["work_mode"])


def downgrade() -> None:
    op.drop_index("ix_employees_work_mode", table_name="employees")
    op.drop_column("attendance_records", "work_mode")
    op.drop_column("employees", "work_mode")
