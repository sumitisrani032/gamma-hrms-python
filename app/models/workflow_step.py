import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, DateTime, Integer, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.workflow_definition import WorkflowDefinition
    from app.models.workflow_step_instance import WorkflowStepInstance


class WorkflowStep(Base):
    __tablename__ = "workflow_steps"

    APPROVER_TYPES = ("specific_user", "role", "reporting_manager", "department_head")
    REJECT_ACTIONS = ("terminate", "send_back", "skip")

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    workflow_definition_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    approver_type: Mapped[str] = mapped_column(String(50), nullable=False)
    approver_value: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    action_on_reject: Mapped[str] = mapped_column(String(20), nullable=False)
    auto_escalation_hours: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    workflow_definition: Mapped["WorkflowDefinition"] = relationship("WorkflowDefinition")
    workflow_step_instances: Mapped[list["WorkflowStepInstance"]] = relationship("WorkflowStepInstance", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_workflow_steps_def_order", "workflow_definition_id", "step_order", unique=True),
    )

    @validates("step_order")
    def validate_step_order(self, key: str, value: int) -> int:
        if value is None:
            raise ValueError("Step order cannot be empty")
        if value <= 0:
            raise ValueError("Step order must be greater than 0")
        return value

    @validates("approver_type")
    def validate_approver_type(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Approver type cannot be empty")
        if len(value) > 50:
            raise ValueError("Approver type is too long (maximum is 50 characters)")
        return value

    @validates("action_on_reject")
    def validate_action_on_reject(self, key: str, value: str) -> str:
        if value not in self.REJECT_ACTIONS:
            raise ValueError(f"Action on reject must be one of {self.REJECT_ACTIONS}")
        return value

    @validates("auto_escalation_hours")
    def validate_auto_escalation_hours(self, key: str, value: Optional[int]) -> Optional[int]:
        if value is not None and value <= 0:
            raise ValueError("Auto escalation hours must be greater than 0")
        return value
