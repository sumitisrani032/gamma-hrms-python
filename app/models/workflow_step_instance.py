import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, DateTime, Text, Index, Select, select
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.workflow_instance import WorkflowInstance
    from app.models.workflow_step import WorkflowStep
    from app.models.user import User


class WorkflowStepInstance(Base):
    __tablename__ = "workflow_step_instances"

    STATUSES = ("pending", "approved", "rejected", "skipped", "escalated")

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    workflow_instance_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    workflow_step_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    assigned_to_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    acted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    workflow_instance: Mapped["WorkflowInstance"] = relationship("WorkflowInstance")
    workflow_step: Mapped["WorkflowStep"] = relationship("WorkflowStep")
    assigned_to: Mapped[Optional["User"]] = relationship("User")

    __table_args__ = (
        Index("index_workflow_step_instances_on_status", "status"),
        Index("index_workflow_step_instances_on_assigned_to_id", "assigned_to_id"),
        Index("index_workflow_step_instances_on_workflow_instance_id", "workflow_instance_id"),
        Index("index_workflow_step_instances_on_workflow_step_id", "workflow_step_id"),
    )

    @classmethod
    def pending(cls) -> Select:
        return select(cls).where(cls.status == "pending")

    def is_pending(self) -> bool:
        return self.status == "pending"

    def acted(self) -> bool:
        return self.acted_at is not None

    @validates("status")
    def validate_status(self, key: str, value: str) -> str:
        if value is None:
            raise ValueError("Status cannot be empty")
        if value not in self.STATUSES:
            raise ValueError(f"Status must be one of {self.STATUSES}")
        return value
