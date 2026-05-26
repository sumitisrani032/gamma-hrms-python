import uuid
from datetime import datetime, date
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, Text, Integer, Date, Index, Select, select
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base
from app.models.mixins import TenantMixin, AuditableMixin

if TYPE_CHECKING:
    from app.models.attachment import Attachment
    from app.models.user import User
    from app.models.policy_acknowledgement import PolicyAcknowledgement


class PolicyDocument(TenantMixin, AuditableMixin, Base):
    __tablename__ = "policy_documents"

    CATEGORIES = ("hr_policy", "code_of_conduct", "compliance", "safety", "travel", "benefits", "other")
    STATUSES = ("draft", "published", "archived")
    APPLICABLE_SCOPES = ("all", "department", "location", "grade")

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    attachment_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    published_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    previous_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    acknowledgement_required: Mapped[bool] = mapped_column(Boolean, nullable=False)
    effective_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    applicable_to: Mapped[str] = mapped_column(String(20), nullable=False)
    applicable_ids: Mapped[list] = mapped_column(JSONB, nullable=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    attachment: Mapped["Attachment"] = relationship("Attachment")
    published_by: Mapped[Optional["User"]] = relationship("User")
    previous_version: Mapped[Optional["PolicyDocument"]] = relationship("PolicyDocument", remote_side="PolicyDocument.id")
    acknowledgements: Mapped[list["PolicyAcknowledgement"]] = relationship("PolicyAcknowledgement", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_policy_docs_tenant_title_version", "tenant_id", "title", "version_number", unique=True),
        Index("index_policy_documents_on_attachment_id", "attachment_id"),
        Index("index_policy_documents_on_category", "category"),
        Index("index_policy_documents_on_status", "status"),
    )

    @classmethod
    def published(cls) -> Select:
        return select(cls).where(cls.status == "published")

    @classmethod
    def active(cls) -> Select:
        return cls.published().where(
            (cls.expiry_date.is_(None)) | (cls.expiry_date >= date.today())
        )

    @classmethod
    def requiring_acknowledgement(cls) -> Select:
        return select(cls).where(cls.acknowledgement_required)

    @classmethod
    def by_category(cls, category: str) -> Select:
        return select(cls).where(cls.category == category)

    def is_published(self) -> bool:
        return self.status == "published"

    def applicable_to_employee(self, employee) -> bool:
        if self.applicable_to == "all":
            return True
        mapping = {
            "department": employee.department_id,
            "location": employee.location_id,
            "grade": employee.grade_id,
        }
        return mapping.get(self.applicable_to) in self.applicable_ids

    def acknowledgement_stats(self) -> dict:
        total = len(self.acknowledgements)
        acknowledged = sum(1 for a in self.acknowledgements if a.status == "acknowledged")
        return {"total": total, "acknowledged": acknowledged, "pending": total - acknowledged}

    @validates("title")
    def validate_title(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Title cannot be empty")
        if len(value) > 255:
            raise ValueError("Title is too long (maximum is 255 characters)")
        return value

    @validates("category")
    def validate_category(self, key: str, value: str) -> str:
        if value not in self.CATEGORIES:
            raise ValueError(f"Category must be one of {self.CATEGORIES}")
        return value

    @validates("status")
    def validate_status(self, key: str, value: str) -> str:
        if value is None:
            raise ValueError("Status cannot be empty")
        if value not in self.STATUSES:
            raise ValueError(f"Status must be one of {self.STATUSES}")
        return value

    @validates("applicable_to")
    def validate_applicable_to(self, key: str, value: str) -> str:
        if value not in self.APPLICABLE_SCOPES:
            raise ValueError(f"Applicable to must be one of {self.APPLICABLE_SCOPES}")
        return value

    @validates("version_number")
    def validate_version_number(self, key: str, value: int) -> int:
        if value is None:
            raise ValueError("Version number cannot be empty")
        if value <= 0:
            raise ValueError("Version number must be greater than 0")
        return value
