import uuid
from datetime import datetime, date
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, DateTime, Text, Numeric, Date, Index, Select, select, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates, object_session

from app.db.base import Base
from app.models.mixins import TenantMixin, AuditableMixin

if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.leave_type import LeaveType
    from app.models.workflow_instance import WorkflowInstance
    from app.models.user import User


class LeaveRequest(TenantMixin, AuditableMixin, Base):
    __tablename__ = "leave_requests"

    STATUSES = ("pending", "approved", "rejected", "cancelled", "withdrawn")
    HALF_DAY_OPTIONS = ("first_half", "second_half")

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    employee_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    leave_type_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("leave_types.id"), nullable=False)
    start_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    end_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    start_half: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    end_half: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    number_of_days: Mapped[float] = mapped_column(Numeric(5, 1), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    workflow_instance_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("workflow_instances.id"), nullable=True)
    approved_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cancellation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    employee: Mapped["Employee"] = relationship("Employee")
    leave_type: Mapped["LeaveType"] = relationship("LeaveType")
    workflow_instance: Mapped[Optional["WorkflowInstance"]] = relationship("WorkflowInstance")
    approved_by: Mapped[Optional["User"]] = relationship("User")

    __table_args__ = (
        Index("idx_leave_requests_dates", "start_date", "end_date"),
        Index("index_leave_requests_on_employee_id", "employee_id"),
        Index("index_leave_requests_on_leave_type_id", "leave_type_id"),
        Index("index_leave_requests_on_status", "status"),
        Index("index_leave_requests_on_tenant_id", "tenant_id"),
    )

    @classmethod
    def pending(cls) -> Select:
        return select(cls).where(cls.status == "pending")

    @classmethod
    def approved(cls) -> Select:
        return select(cls).where(cls.status == "approved")

    @classmethod
    def active(cls) -> Select:
        return select(cls).where(cls.status.in_(["pending", "approved"]))

    @classmethod
    def in_range(cls, from_date: date, to_date: date) -> Select:
        return select(cls).where(cls.start_date <= to_date, cls.end_date >= from_date)

    @classmethod
    def for_employee(cls, emp_id: uuid.UUID) -> Select:
        return select(cls).where(cls.employee_id == emp_id)

    @validates("number_of_days")
    def validate_number_of_days(self, key: str, value: float) -> float:
        if value is None:
            raise ValueError("Number of days cannot be empty")
        if value <= 0:
            raise ValueError("Number of days must be greater than 0")
        return value

    @validates("status")
    def validate_status(self, key: str, value: str) -> str:
        if value not in self.STATUSES:
            raise ValueError(f"Status must be one of {self.STATUSES}")
        return value

    @validates("start_half")
    def validate_start_half(self, key: str, value: Optional[str]) -> Optional[str]:
        if value is not None and value not in self.HALF_DAY_OPTIONS:
            raise ValueError(f"Start half must be one of {self.HALF_DAY_OPTIONS}")
        return value

    @validates("end_half")
    def validate_end_half(self, key: str, value: Optional[str]) -> Optional[str]:
        if value is not None and value not in self.HALF_DAY_OPTIONS:
            raise ValueError(f"End half must be one of {self.HALF_DAY_OPTIONS}")
        return value

    @validates("employee_id", "start_date", "end_date")
    def validate_no_overlap(self, key: str, value):
        if key == "start_date" and value is None:
            raise ValueError("Start date cannot be empty")
        if key == "end_date":
            if value is None:
                raise ValueError("End date cannot be empty")
            if self.start_date is not None and value < self.start_date:
                raise ValueError("End date must be on or after start date")
        if self.employee_id is not None and self.start_date is not None and self.end_date is not None:
            session = object_session(self)
            if session is not None:
                overlapping = session.execute(
                    select(LeaveRequest.id).where(
                        LeaveRequest.status.in_(["pending", "approved"]),
                        LeaveRequest.employee_id == self.employee_id,
                        LeaveRequest.start_date <= self.end_date,
                        LeaveRequest.end_date >= self.start_date,
                        LeaveRequest.id != self.id,
                    ).limit(1)
                ).first()
                if overlapping is not None:
                    raise ValueError("Overlapping leave request already exists for these dates")
        return value
