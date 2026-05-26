import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Boolean, DateTime, Text, Integer, Index, Select, select
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base
from app.models.employee_document import EmployeeDocument
from app.models.mixins import TenantMixin, AuditableMixin, restrict_on_delete


class DocumentRequirement(TenantMixin, AuditableMixin, Base):
    __tablename__ = "document_requirements"

    APPLICABLE_SCOPES = ("all", "department", "location", "grade")

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    applicable_to: Mapped[str] = mapped_column(String(20), nullable=False)
    applicable_ids: Mapped[list] = mapped_column(JSONB, nullable=False)
    has_expiry: Mapped[bool] = mapped_column(Boolean, nullable=False)
    allowed_file_types: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    max_file_size_mb: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    employee_documents: Mapped[list["EmployeeDocument"]] = relationship("EmployeeDocument")

    __table_args__ = (
        Index("idx_doc_requirements_tenant_name", "tenant_id", "name", unique=True),
        Index("index_document_requirements_on_document_type", "document_type"),
        Index("index_document_requirements_on_tenant_id", "tenant_id"),
    )

    @classmethod
    def active(cls) -> Select:
        return select(cls).where(cls.is_active)

    @classmethod
    def mandatory(cls) -> Select:
        return select(cls).where(cls.is_mandatory)

    @validates("name")
    def validate_name(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Name cannot be empty")
        if len(value) > 255:
            raise ValueError("Name is too long (maximum is 255 characters)")
        return value

    @validates("document_type")
    def validate_document_type(self, key: str, value: str) -> str:
        if value not in EmployeeDocument.DOCUMENT_TYPES:
            raise ValueError(f"Document type must be one of {EmployeeDocument.DOCUMENT_TYPES}")
        return value

    @validates("applicable_to")
    def validate_applicable_to(self, key: str, value: str) -> str:
        if value not in self.APPLICABLE_SCOPES:
            raise ValueError(f"Applicable to must be one of {self.APPLICABLE_SCOPES}")
        return value

    def applicable_to_employee(self, employee) -> bool:
        if self.applicable_to == "all":
            return True
        mapping = {
            "department": employee.department_id,
            "location": employee.location_id,
            "grade": employee.grade_id,
        }
        return mapping.get(self.applicable_to) in self.applicable_ids


restrict_on_delete(DocumentRequirement, EmployeeDocument, EmployeeDocument.document_requirement_id)
