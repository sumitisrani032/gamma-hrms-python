import uuid
from datetime import datetime, date
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, Text, Numeric, Date, Integer, Index, Select, select, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base
from app.models.mixins import TenantMixin

if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.shift import Shift
    from app.models.attendance_session import AttendanceSession
    from app.models.attendance_regularization import AttendanceRegularization


class AttendanceRecord(TenantMixin, Base):
    __tablename__ = "attendance_records"

    STATUSES = ["present", "absent", "half_day", "on_leave", "holiday", "weekly_off", "comp_off", "regularized"]
    SOURCES = ["manual", "biometric", "web", "mobile", "system"]
    WORK_MODES = ["office", "wfh"]
    WORK_MODE_SOURCES = ["auto", "request", "manual"]

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    shift_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("shifts.id", ondelete="SET NULL"), nullable=True)
    date: Mapped[datetime] = mapped_column(Date, nullable=False)
    clock_in: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    clock_out: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    total_hours: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    effective_hours: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    source: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_late: Mapped[bool] = mapped_column(Boolean, nullable=False)
    late_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_early_departure: Mapped[bool] = mapped_column(Boolean, nullable=False)
    overtime_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_regularized: Mapped[bool] = mapped_column(Boolean, nullable=False)
    work_mode: Mapped[str] = mapped_column(String(20), nullable=False)
    work_mode_source: Mapped[str] = mapped_column(String(20), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", back_populates="attendance_records")
    shift: Mapped[Optional["Shift"]] = relationship("Shift", back_populates="attendance_records")
    sessions: Mapped[list["AttendanceSession"]] = relationship("AttendanceSession", back_populates="attendance_record", cascade="all, delete-orphan")
    attendance_regularizations: Mapped[list["AttendanceRegularization"]] = relationship("AttendanceRegularization", back_populates="attendance_record", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_attendance_records_unique", "tenant_id", "employee_id", "date", unique=True),
        Index("index_attendance_records_on_status", "status"),
        Index("index_attendance_records_on_date", "date"),
        Index("index_attendance_records_on_employee_id", "employee_id"),
        Index("index_attendance_records_on_shift_id", "shift_id"),
        Index("index_attendance_records_on_tenant_id", "tenant_id"),
    )

    # Scopes
    @classmethod
    def for_date(cls, target_date: date) -> Select:
        return select(cls).where(cls.date == target_date)

    @classmethod
    def for_month(cls, year: int, month: int) -> Select:
        start = date(year, month, 1)
        end = date(year, month, 28)
        import calendar
        end = date(year, month, calendar.monthrange(year, month)[1])
        return select(cls).where(cls.date.between(start, end))

    @classmethod
    def present_days(cls) -> Select:
        return select(cls).where(cls.status.in_(["present", "half_day", "regularized"]))

    # Validators
    @validates("status")
    def validate_status(self, key, value):
        if value not in self.STATUSES:
            raise ValueError(f"Invalid status '{value}'. Must be one of {self.STATUSES}")
        return value

    @validates("source")
    def validate_source(self, key, value):
        if value is not None and value not in self.SOURCES:
            raise ValueError(f"Invalid source '{value}'. Must be one of {self.SOURCES}")
        return value

    @validates("work_mode")
    def validate_work_mode(self, key, value):
        if value is not None and value not in self.WORK_MODES:
            raise ValueError(f"Invalid work_mode '{value}'. Must be one of {self.WORK_MODES}")
        return value

    @validates("work_mode_source")
    def validate_work_mode_source(self, key, value):
        if value is not None and value not in self.WORK_MODE_SOURCES:
            raise ValueError(f"Invalid work_mode_source '{value}'. Must be one of {self.WORK_MODE_SOURCES}")
        return value

    # Methods
    def compute_hours(self) -> None:
        if not self.clock_in or not self.clock_out:
            return
        delta = (self.clock_out - self.clock_in).total_seconds()
        self.total_hours = round(delta / 3600.0, 2)
        self.effective_hours = self.total_hours
