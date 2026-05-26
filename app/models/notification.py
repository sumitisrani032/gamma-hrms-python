import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, Text, Index, ForeignKey, Select, select
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates, object_session

from app.db.base import Base
from app.models.mixins import TenantMixin


if TYPE_CHECKING:
    from app.models.user import User


class Notification(TenantMixin, Base):
    __tablename__ = "notifications"

    TYPES = ("workflow_action", "workflow_complete", "info", "warning", "system")

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notification_type: Mapped[str] = mapped_column(String(50), nullable=False)
    reference_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    reference_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    user: Mapped["User"] = relationship("User")

    __table_args__ = (
        Index("idx_notifications_user_read", "user_id", "is_read"),
        Index("idx_notifications_reference", "reference_type", "reference_id"),
        Index("index_notifications_on_user_id", "user_id"),
        Index("index_notifications_on_tenant_id", "tenant_id"),
    )

    @classmethod
    def unread(cls) -> Select:
        return select(cls).where(~cls.is_read)

    @classmethod
    def recent(cls) -> Select:
        return select(cls).order_by(cls.created_at.desc())

    @validates("title")
    def validate_title(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Title cannot be empty")
        if len(value) > 255:
            raise ValueError("Title is too long (maximum is 255 characters)")
        return value

    @validates("notification_type")
    def validate_notification_type(self, key: str, value: str) -> str:
        if value not in self.TYPES:
            raise ValueError(f"Notification type must be one of {self.TYPES}")
        return value

    def read(self) -> bool:
        return self.is_read

    def mark_read(self) -> None:
        if not self.read():
            self.is_read = True
            self.read_at = datetime.utcnow()
            object_session(self).flush()
