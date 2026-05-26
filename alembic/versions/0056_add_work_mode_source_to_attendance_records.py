"""add work mode source to attendance records (Rails: 20260415120005_add_work_mode_source_to_attendance_records)

Revision ID: 0056
Revises: 0055
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa

revision = "0056"
down_revision = "0055"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("attendance_records", sa.Column("work_mode_source", sa.String(length=20), nullable=False, server_default=sa.text("'auto'")))


def downgrade() -> None:
    op.drop_column("attendance_records", "work_mode_source")
