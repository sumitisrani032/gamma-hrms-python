import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, DateTime, Text, Date, Index, Select, select, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base
from app.models.mixins import TenantMixin

if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.user import User
    from app.models.workflow_instance import WorkflowInstance


class EmployeeLifecycleEvent(TenantMixin, Base):
    __tablename__ = "employee_lifecycle_events"

    EVENT_TYPES = ("joining", "confirmation", "promotion", "transfer", "designation_change", "grade_change",
                   "department_change", "manager_change", "separation", "probation_extension")

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    employee_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    event_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    effective_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    previous_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    new_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    performed_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    workflow_instance_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("workflow_instances.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    employee: Mapped["Employee"] = relationship("Employee")
    performed_by: Mapped[Optional["User"]] = relationship("User")
    workflow_instance: Mapped[Optional["WorkflowInstance"]] = relationship("WorkflowInstance")

    __table_args__ = (
        Index("index_employee_lifecycle_events_on_employee_id", "employee_id"),
        Index("index_employee_lifecycle_events_on_event_date", "event_date"),
        Index("index_employee_lifecycle_events_on_event_type", "event_type"),
        Index("index_employee_lifecycle_events_on_tenant_id", "tenant_id"),
    )

    @classmethod
    def recent(cls) -> Select:
        return select(cls).order_by(cls.event_date.desc())

    @classmethod
    def by_type(cls, event_type: str) -> Select:
        return select(cls).where(cls.event_type == event_type)

    @validates("event_type")
    def validate_event_type(self, key: str, value: str) -> str:
        if value not in self.EVENT_TYPES:
            raise ValueError(f"Event type must be one of {self.EVENT_TYPES}")
        return value

    @validates("event_date")
    def validate_event_date(self, key: str, value: datetime) -> datetime:
        if value is None:
            raise ValueError("Event date cannot be empty")
        return value

    @validates("effective_date")
    def validate_effective_date(self, key: str, value: datetime) -> datetime:
        if value is None:
            raise ValueError("Effective date cannot be empty")
        return value
