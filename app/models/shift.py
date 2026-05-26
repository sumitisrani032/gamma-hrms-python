import uuid
from datetime import datetime, date
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, Time, Integer, Numeric, Index, Select, select
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base
from app.models.mixins import TenantMixin, AuditableMixin, restrict_on_delete

if TYPE_CHECKING:
    from app.models.shift_assignment import ShiftAssignment
    from app.models.attendance_record import AttendanceRecord


class Shift(TenantMixin, AuditableMixin, Base):
    __tablename__ = "shifts"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    start_time: Mapped[datetime] = mapped_column(Time, nullable=False)
    end_time: Mapped[datetime] = mapped_column(Time, nullable=False)
    grace_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    half_day_hours: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), nullable=True)
    full_day_hours: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    is_night_shift: Mapped[bool] = mapped_column(Boolean, nullable=False)
    weekly_offs: Mapped[list] = mapped_column(JSONB, nullable=False)
    is_flexible: Mapped[bool] = mapped_column(Boolean, nullable=False)
    min_hours: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    shift_assignments: Mapped[list["ShiftAssignment"]] = relationship("ShiftAssignment")
    attendance_records: Mapped[list["AttendanceRecord"]] = relationship("AttendanceRecord")

    __table_args__ = (
        Index("index_shifts_on_tenant_id_and_name", "tenant_id", "name", unique=True),
    )

    @classmethod
    def active(cls) -> Select:
        return select(cls).where(cls.is_active)

    @classmethod
    def default_shift(cls) -> Select:
        return select(cls).where(cls.is_default)

    def weekly_off(self, target_date: date) -> bool:
        day_name = target_date.strftime("%A").lower()
        return day_name in self.weekly_offs

    def shift_duration_hours(self) -> float:
        start_seconds = self.start_time.hour * 3600 + self.start_time.minute * 60 + self.start_time.second
        end_seconds = self.end_time.hour * 3600 + self.end_time.minute * 60 + self.end_time.second
        if self.is_night_shift and end_seconds < start_seconds:
            end_seconds += 86400
        return (end_seconds - start_seconds) / 3600.0

    @validates("name")
    def validate_name(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Name cannot be empty")
        if len(value) > 255:
            raise ValueError("Name is too long (maximum is 255 characters)")
        return value

    @validates("start_time")
    def validate_start_time(self, key: str, value: datetime) -> datetime:
        if value is None:
            raise ValueError("Start time cannot be empty")
        return value

    @validates("end_time")
    def validate_end_time(self, key: str, value: datetime) -> datetime:
        if value is None:
            raise ValueError("End time cannot be empty")
        return value

    @validates("full_day_hours")
    def validate_full_day_hours(self, key: str, value: float) -> float:
        if value is None:
            raise ValueError("Full day hours cannot be empty")
        if value <= 0:
            raise ValueError("Full day hours must be greater than 0")
        return value

    @validates("grace_minutes")
    def validate_grace_minutes(self, key: str, value: int) -> int:
        if value is not None and value < 0:
            raise ValueError("Grace minutes must be greater than or equal to 0")
        return value


from app.models.shift_assignment import ShiftAssignment  # noqa: E402
from app.models.attendance_record import AttendanceRecord  # noqa: E402
restrict_on_delete(Shift, ShiftAssignment, ShiftAssignment.shift_id)  # noqa: E402
restrict_on_delete(Shift, AttendanceRecord, AttendanceRecord.shift_id)  # noqa: E402
