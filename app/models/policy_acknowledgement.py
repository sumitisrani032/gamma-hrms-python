import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, DateTime, Text, Index, Select, select
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates, object_session

from app.db.base import Base
from app.models.mixins import TenantMixin

if TYPE_CHECKING:
    from app.models.policy_document import PolicyDocument
    from app.models.employee import Employee


class PolicyAcknowledgement(TenantMixin, Base):
    __tablename__ = "policy_acknowledgements"

    STATUSES = ("pending", "acknowledged")

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    policy_document_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    employee_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    policy_document: Mapped["PolicyDocument"] = relationship("PolicyDocument")
    employee: Mapped["Employee"] = relationship("Employee")

    __table_args__ = (
        Index("idx_policy_acks_unique", "tenant_id", "policy_document_id", "employee_id", unique=True),
        Index("index_policy_acknowledgements_on_employee_id", "employee_id"),
        Index("index_policy_acknowledgements_on_policy_document_id", "policy_document_id"),
        Index("index_policy_acknowledgements_on_status", "status"),
    )

    @classmethod
    def pending(cls) -> Select:
        return select(cls).where(cls.status == "pending")

    @classmethod
    def acknowledged(cls) -> Select:
        return select(cls).where(cls.status == "acknowledged")

    def acknowledge(self, ip_address: str = None) -> None:
        self.status = "acknowledged"
        self.acknowledged_at = datetime.utcnow()
        self.ip_address = ip_address
        object_session(self).flush()

    @validates("status")
    def validate_status(self, key: str, value: str) -> str:
        if value is None:
            raise ValueError("Status cannot be empty")
        if value not in self.STATUSES:
            raise ValueError(f"Status must be one of {self.STATUSES}")
        return value
