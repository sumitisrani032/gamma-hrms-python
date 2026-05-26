import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, DateTime, Numeric, Integer, Index, Select, select, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TenantMixin

if TYPE_CHECKING:
    from app.models.attendance_record import AttendanceRecord
    from app.models.employee import Employee


class AttendanceSession(TenantMixin, Base):
    __tablename__ = "attendance_sessions"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attendance_record_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("attendance_records.id", ondelete="CASCADE"), nullable=False)
    employee_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    clock_in: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    clock_out: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    hours: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    session_number: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    attendance_record: Mapped["AttendanceRecord"] = relationship("AttendanceRecord", back_populates="sessions")
    employee: Mapped["Employee"] = relationship("Employee")

    __table_args__ = (
        Index("idx_att_sessions_record_number", "attendance_record_id", "session_number", unique=True),
        Index("index_attendance_sessions_on_attendance_record_id", "attendance_record_id"),
        Index("index_attendance_sessions_on_employee_id", "employee_id"),
        Index("index_attendance_sessions_on_tenant_id", "tenant_id"),
    )

    # Scopes
    @classmethod
    def open(cls) -> Select:
        return select(cls).where(cls.clock_out.is_(None))

    @classmethod
    def closed(cls) -> Select:
        return select(cls).where(cls.clock_out.isnot(None))

    @classmethod
    def ordered(cls) -> Select:
        return select(cls).order_by(cls.session_number)

    # Methods
    def is_open(self) -> bool:
        return self.clock_out is None

    def compute_hours(self) -> None:
        if not self.clock_in or not self.clock_out:
            return
        delta = (self.clock_out - self.clock_in).total_seconds()
        self.hours = round(delta / 3600.0, 2)
