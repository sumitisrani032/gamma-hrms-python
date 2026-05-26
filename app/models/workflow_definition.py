import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, Index, Select, select
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base
from app.models.mixins import TenantMixin, restrict_on_delete

if TYPE_CHECKING:
    from app.models.workflow_step import WorkflowStep
    from app.models.workflow_instance import WorkflowInstance


class WorkflowDefinition(TenantMixin, Base):
    __tablename__ = "workflow_definitions"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    workflow_steps: Mapped[list["WorkflowStep"]] = relationship("WorkflowStep", cascade="all, delete-orphan")
    workflow_instances: Mapped[list["WorkflowInstance"]] = relationship("WorkflowInstance")

    __table_args__ = (
        Index("idx_workflow_defs_tenant_entity", "tenant_id", "entity_type"),
    )

    @classmethod
    def active(cls) -> Select:
        return select(cls).where(cls.is_active)

    @classmethod
    def for_entity(cls, entity_type: str) -> Select:
        return select(cls).where(cls.entity_type == entity_type)

    def is_active_workflow(self) -> bool:
        return self.is_active

    def steps_count(self) -> int:
        return len(self.workflow_steps)

    @validates("name")
    def validate_name(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Name cannot be empty")
        if len(value) > 255:
            raise ValueError("Name is too long (maximum is 255 characters)")
        return value

    @validates("entity_type")
    def validate_entity_type(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Entity type cannot be empty")
        if len(value) > 100:
            raise ValueError("Entity type is too long (maximum is 100 characters)")
        return value


from app.models.workflow_instance import WorkflowInstance  # noqa: E402
restrict_on_delete(WorkflowDefinition, WorkflowInstance, WorkflowInstance.workflow_definition_id)  # noqa: E402
