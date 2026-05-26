import uuid
from datetime import datetime
from typing import Optional, Any, TYPE_CHECKING

from sqlalchemy import String, DateTime, Text, Index, ForeignKey, Select, select
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB, INET
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TenantMixin

if TYPE_CHECKING:
    from app.models.user import User


class AuditLog(TenantMixin, Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    changes_data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(INET, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User")

    __table_args__ = (
        Index("index_audit_logs_on_user_id", "user_id"),
        Index("idx_audit_logs_resource", "resource_type", "resource_id"),
        Index("index_audit_logs_on_action", "action"),
        Index("index_audit_logs_on_created_at", "created_at"),
        Index("index_audit_logs_on_tenant_id", "tenant_id"),
    )

    # Scopes
    @classmethod
    def recent(cls) -> Select:
        return select(cls).order_by(cls.created_at.desc())

    @classmethod
    def for_resource(cls, resource_type: str, resource_id: uuid.UUID) -> Select:
        return select(cls).where(cls.resource_type == resource_type, cls.resource_id == resource_id)

    @classmethod
    def by_user(cls, user_id: uuid.UUID) -> Select:
        return select(cls).where(cls.user_id == user_id)

    @classmethod
    def by_action(cls, action: str) -> Select:
        return select(cls).where(cls.action == action)
