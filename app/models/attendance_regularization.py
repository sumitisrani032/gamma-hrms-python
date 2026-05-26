import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, DateTime, Text, Index, Select, select, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base
from app.models.mixins import TenantMixin

if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.attendance_record import AttendanceRecord
    from app.models.workflow_instance import WorkflowInstance
    from app.models.user import User


class AttendanceRegularization(TenantMixin, Base):
    __tablename__ = "attendance_regularizations"

    STATUSES = ["pending", "approved", "rejected", "cancelled"]

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    attendance_record_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("attendance_records.id", ondelete="CASCADE"), nullable=False)
    original_clock_in: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    original_clock_out: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    requested_clock_in: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    requested_clock_out: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    workflow_instance_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("workflow_instances.id", ondelete="SET NULL"), nullable=True)
    approved_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", back_populates="attendance_regularizations")
    attendance_record: Mapped["AttendanceRecord"] = relationship("AttendanceRecord", back_populates="attendance_regularizations")
    workflow_instance: Mapped[Optional["WorkflowInstance"]] = relationship("WorkflowInstance")
    approved_by: Mapped[Optional["User"]] = relationship("User")

    # Validators
    @validates("status")
    def validate_status(self, key, value):
        if value not in self.STATUSES:
            raise ValueError(f"Invalid status '{value}'. Must be one of {self.STATUSES}")
        return value

    __table_args__ = (
        Index("index_attendance_regularizations_on_status", "status"),
        Index("index_attendance_regularizations_on_attendance_record_id", "attendance_record_id"),
        Index("index_attendance_regularizations_on_employee_id", "employee_id"),
        Index("index_attendance_regularizations_on_tenant_id", "tenant_id"),
    )

    # Scopes
    @classmethod
    def pending(cls) -> Select:
        return select(cls).where(cls.status == "pending")
