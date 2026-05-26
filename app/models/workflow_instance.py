import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, DateTime, Integer, Index, Select, select
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base
from app.models.mixins import TenantMixin

if TYPE_CHECKING:
    from app.models.workflow_definition import WorkflowDefinition
    from app.models.user import User
    from app.models.workflow_step_instance import WorkflowStepInstance


class WorkflowInstance(TenantMixin, Base):
    __tablename__ = "workflow_instances"

    STATUSES = ("pending", "in_progress", "approved", "rejected", "cancelled")

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    workflow_definition_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    initiated_by_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    current_step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    workflow_definition: Mapped["WorkflowDefinition"] = relationship("WorkflowDefinition")
    initiated_by: Mapped["User"] = relationship("User")
    workflow_step_instances: Mapped[list["WorkflowStepInstance"]] = relationship("WorkflowStepInstance", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_workflow_instances_entity", "entity_type", "entity_id"),
        Index("index_workflow_instances_on_status", "status"),
        Index("index_workflow_instances_on_initiated_by_id", "initiated_by_id"),
        Index("index_workflow_instances_on_workflow_definition_id", "workflow_definition_id"),
    )

    @classmethod
    def active(cls) -> Select:
        return select(cls).where(cls.status.in_(["pending", "in_progress"]))

    @classmethod
    def for_entity(cls, entity_type: str, entity_id: uuid.UUID) -> Select:
        return select(cls).where(cls.entity_type == entity_type, cls.entity_id == entity_id)

    def completed(self) -> bool:
        return self.status in ("approved", "rejected", "cancelled")

    def current_step_instance(self):
        from app.models.workflow_step_instance import WorkflowStepInstance
        from app.models.workflow_step import WorkflowStep
        stmt = (
            select(WorkflowStepInstance)
            .join(WorkflowStepInstance.workflow_step)
            .where(
                WorkflowStepInstance.workflow_instance_id == self.id,
                WorkflowStep.step_order == self.current_step_order,
            )
            .order_by(WorkflowStepInstance.created_at.desc())
            .limit(1)
        )
        return stmt

    @validates("entity_type")
    def validate_entity_type(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Entity type cannot be empty")
        if len(value) > 100:
            raise ValueError("Entity type is too long (maximum is 100 characters)")
        return value

    @validates("entity_id")
    def validate_entity_id(self, key: str, value: uuid.UUID) -> uuid.UUID:
        if value is None:
            raise ValueError("Entity ID cannot be empty")
        return value

    @validates("current_step_order")
    def validate_current_step_order(self, key: str, value: int) -> int:
        if value is None:
            raise ValueError("Current step order cannot be empty")
        if value <= 0:
            raise ValueError("Current step order must be greater than 0")
        return value

    @validates("status")
    def validate_status(self, key: str, value: str) -> str:
        if value is None:
            raise ValueError("Status cannot be empty")
        if value not in self.STATUSES:
            raise ValueError(f"Status must be one of {self.STATUSES}")
        return value
