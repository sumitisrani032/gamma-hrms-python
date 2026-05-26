import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, Text, Index, Select, select, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates, object_session

from app.db.base import Base
from app.models.mixins import TenantMixin, AuditableMixin

if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.attachment import Attachment
    from app.models.user import User
    from app.models.document_requirement import DocumentRequirement


class EmployeeDocument(TenantMixin, AuditableMixin, Base):
    __tablename__ = "employee_documents"

    DOCUMENT_TYPES = ("id_proof", "address_proof", "education", "experience", "offer_letter", "relieving_letter", "payslip", "pan", "aadhaar", "passport", "bank_proof", "other")
    STATUSES = ("pending", "verified", "rejected", "expired")

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    employee_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    attachment_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("attachments.id"), nullable=False)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    document_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False)
    verified_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    document_requirement_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("document_requirements.id"), nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    employee: Mapped["Employee"] = relationship("Employee")
    attachment: Mapped["Attachment"] = relationship("Attachment")
    verified_by: Mapped[Optional["User"]] = relationship("User")
    document_requirement: Mapped[Optional["DocumentRequirement"]] = relationship("DocumentRequirement")

    __table_args__ = (
        Index("idx_emp_docs_tenant_emp_req", "tenant_id", "employee_id", "document_requirement_id", unique=True, postgresql_where=text("document_requirement_id IS NOT NULL")),
        Index("index_employee_documents_on_attachment_id", "attachment_id"),
        Index("index_employee_documents_on_document_requirement_id", "document_requirement_id"),
        Index("index_employee_documents_on_document_type", "document_type"),
        Index("index_employee_documents_on_employee_id", "employee_id"),
        Index("index_employee_documents_on_status", "status"),
        Index("index_employee_documents_on_tenant_id", "tenant_id"),
    )

    @classmethod
    def is_verified(cls) -> Select:
        return select(cls).where(cls.status == "verified")

    @classmethod
    def pending_verification(cls) -> Select:
        return select(cls).where(cls.status == "pending")

    @classmethod
    def rejected(cls) -> Select:
        return select(cls).where(cls.status == "rejected")

    @classmethod
    def for_requirement(cls, req_id: uuid.UUID) -> Select:
        return select(cls).where(cls.document_requirement_id == req_id)

    @validates("document_type")
    def validate_document_type(self, key: str, value: str) -> str:
        if value not in self.DOCUMENT_TYPES:
            raise ValueError(f"Document type must be one of {self.DOCUMENT_TYPES}")
        return value

    @validates("document_name")
    def validate_document_name(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Document name cannot be empty")
        if len(value) > 255:
            raise ValueError("Document name is too long (maximum is 255 characters)")
        return value

    @validates("status")
    def validate_status(self, key: str, value: str) -> str:
        if value not in self.STATUSES:
            raise ValueError(f"Status must be one of {self.STATUSES}")
        return value

    def verify(self, user: "User") -> None:
        self.verified = True
        self.status = "verified"
        self.verified_by = user
        self.verified_at = datetime.utcnow()
        self.rejection_reason = None
        object_session(self).flush()

    def reject(self, user: "User", reason: str) -> None:
        self.verified = False
        self.status = "rejected"
        self.verified_by = user
        self.verified_at = datetime.utcnow()
        self.rejection_reason = reason
        object_session(self).flush()
