import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, Numeric, Index, Select, select, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base
from app.models.mixins import TenantMixin

if TYPE_CHECKING:
    from app.models.employee import Employee


class AttendanceSummary(TenantMixin, Base):
    __tablename__ = "attendance_summaries"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    total_working_days: Mapped[int] = mapped_column(Integer, nullable=False)
    days_present: Mapped[int] = mapped_column(Integer, nullable=False)
    days_absent: Mapped[int] = mapped_column(Integer, nullable=False)
    days_half_day: Mapped[int] = mapped_column(Integer, nullable=False)
    days_on_leave: Mapped[int] = mapped_column(Integer, nullable=False)
    days_holiday: Mapped[int] = mapped_column(Integer, nullable=False)
    days_weekly_off: Mapped[int] = mapped_column(Integer, nullable=False)
    total_hours_worked: Mapped[float] = mapped_column(Numeric(7, 2), nullable=False)
    total_overtime_hours: Mapped[float] = mapped_column(Numeric(7, 2), nullable=False)
    late_count: Mapped[int] = mapped_column(Integer, nullable=False)
    early_exit_count: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", back_populates="attendance_summaries")

    # Validators
    @validates("month")
    def validate_month(self, key, value):
        if value not in range(1, 13):
            raise ValueError("month must be between 1 and 12")
        return value

    __table_args__ = (
        Index("idx_attendance_summaries_unique", "tenant_id", "employee_id", "year", "month", unique=True),
        Index("index_attendance_summaries_on_employee_id", "employee_id"),
        Index("index_attendance_summaries_on_tenant_id", "tenant_id"),
    )

    # Scopes
    @classmethod
    def for_month(cls, year: int, month: int) -> Select:
        return select(cls).where(cls.year == year, cls.month == month)
