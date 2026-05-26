import uuid
from datetime import datetime, date
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, DateTime, Text, Date, Index, Select, select
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base
from app.models.mixins import TenantMixin

if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.wfh_policy import WfhPolicy
    from app.models.workflow_instance import WorkflowInstance


class WfhRequest(TenantMixin, Base):
    __tablename__ = "wfh_requests"

    STATUSES = ("pending", "approved", "rejected", "cancelled")

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    employee_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    wfh_policy_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    workflow_instance_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    date: Mapped[datetime] = mapped_column(Date, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cancellation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    employee: Mapped["Employee"] = relationship("Employee")
    wfh_policy: Mapped[Optional["WfhPolicy"]] = relationship("WfhPolicy")
    workflow_instance: Mapped[Optional["WorkflowInstance"]] = relationship("WorkflowInstance")

    __table_args__ = (
        Index("index_wfh_requests_on_status", "status"),
        Index("index_wfh_requests_on_date", "date"),
        Index("index_wfh_requests_on_employee_id", "employee_id"),
    )

    @classmethod
    def active(cls) -> Select:
        return select(cls).where(cls.status.in_(["pending", "approved"]))

    @classmethod
    def approved(cls) -> Select:
        return select(cls).where(cls.status == "approved")

    @classmethod
    def pending(cls) -> Select:
        return select(cls).where(cls.status == "pending")

    @classmethod
    def for_employee(cls, emp_id: uuid.UUID) -> Select:
        return select(cls).where(cls.employee_id == emp_id)

    @classmethod
    def for_month(cls, year: int, month: int) -> Select:
        start = date(year, month, 1)
        import calendar
        end = date(year, month, calendar.monthrange(year, month)[1])
        return select(cls).where(cls.date.between(start, end))

    @classmethod
    def for_date_range(cls, start_date: date, end_date: date) -> Select:
        return select(cls).where(cls.date.between(start_date, end_date))

    @validates("date")
    def validate_date(self, key: str, value: datetime) -> datetime:
        if value is None:
            raise ValueError("Date cannot be empty")
        return value

    @validates("status")
    def validate_status(self, key: str, value: str) -> str:
        if value is None:
            raise ValueError("Status cannot be empty")
        if value not in self.STATUSES:
            raise ValueError(f"Status must be one of {self.STATUSES}")
        return value
