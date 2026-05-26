import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, DateTime, Index, Select, select
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates, object_session

from app.db.base import Base
from app.models.mixins import TenantMixin

if TYPE_CHECKING:
    from app.models.user import User


class RefreshToken(TenantMixin, Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    token_digest: Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    user: Mapped["User"] = relationship("User")

    __table_args__ = (
        Index("index_refresh_tokens_on_token_digest", "token_digest", unique=True),
        Index("index_refresh_tokens_on_expires_at", "expires_at"),
    )

    @classmethod
    def active(cls) -> Select:
        return select(cls).where(cls.revoked_at.is_(None)).where(cls.expires_at > datetime.utcnow())

    def expired(self) -> bool:
        return self.expires_at < datetime.utcnow()

    def revoked(self) -> bool:
        return self.revoked_at is not None

    def revoke(self) -> None:
        self.revoked_at = datetime.utcnow()
        object_session(self).flush()

    def usable(self) -> bool:
        return not self.expired() and not self.revoked()

    @validates("token_digest")
    def validate_token_digest(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Token digest cannot be empty")
        return value

    @validates("expires_at")
    def validate_expires_at(self, key: str, value: datetime) -> datetime:
        if value is None:
            raise ValueError("Expires at cannot be empty")
        return value
