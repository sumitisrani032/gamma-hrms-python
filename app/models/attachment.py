import uuid
import os
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, DateTime, Text, BigInteger, Index, Select, select
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base
from app.models.mixins import TenantMixin

if TYPE_CHECKING:
    from app.models.user import User


class Attachment(TenantMixin, Base):
    __tablename__ = "attachments"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    uploaded_by_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    s3_key: Mapped[str] = mapped_column(Text, nullable=False)
    entity_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    uploaded_by: Mapped["User"] = relationship("User")

    __table_args__ = (
        Index("idx_attachments_entity", "entity_type", "entity_id"),
        Index("index_attachments_on_uploaded_by_id", "uploaded_by_id"),
    )

    @classmethod
    def for_entity(cls, entity_type: str, entity_id: uuid.UUID) -> Select:
        return select(cls).where(cls.entity_type == entity_type, cls.entity_id == entity_id)

    def image(self) -> bool:
        return self.file_type.startswith("image/") if self.file_type else False

    @property
    def extension(self) -> str:
        return os.path.splitext(self.file_name)[1].lstrip('.')

    @validates("file_name")
    def validate_file_name(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("File name cannot be empty")
        if len(value) > 255:
            raise ValueError("File name is too long (maximum is 255 characters)")
        return value

    @validates("s3_key")
    def validate_s3_key(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("S3 key cannot be empty")
        return value

    @validates("file_type")
    def validate_file_type(self, key: str, value: Optional[str]) -> Optional[str]:
        if value is not None and len(value) > 50:
            raise ValueError("File type is too long (maximum is 50 characters)")
        return value

    @validates("file_size")
    def validate_file_size(self, key: str, value: Optional[int]) -> Optional[int]:
        if value is not None and value <= 0:
            raise ValueError("File size must be greater than 0")
        return value
