import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, DateTime, Text, Index, Select, select, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base
from app.models.mixins import TenantMixin, AuditableMixin, restrict_on_delete

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.employee import Employee


class Department(TenantMixin, AuditableMixin, Base):
    __tablename__ = "departments"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    company_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parent_department_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    head_employee_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Relationships
    company: Mapped["Company"] = relationship("Company")
    parent_department: Mapped[Optional["Department"]] = relationship("Department", remote_side="Department.id")
    sub_departments: Mapped[list["Department"]] = relationship("Department", back_populates="parent_department")
    head_employee: Mapped[Optional["Employee"]] = relationship("Employee", foreign_keys=[head_employee_id])
    employees: Mapped[list["Employee"]] = relationship("Employee", back_populates="department")

    __table_args__ = (
        Index("idx_departments_tenant_company_name", "tenant_id", "company_id", "name", unique=True),
        Index("index_departments_on_company_id", "company_id"),
        Index("index_departments_on_parent_department_id", "parent_department_id"),
        Index("index_departments_on_tenant_id", "tenant_id"),
    )

    # Scopes
    @classmethod
    def active(cls) -> Select:
        return select(cls).where(cls.status == "active")

    @classmethod
    def root_departments(cls) -> Select:
        return select(cls).where(cls.parent_department_id.is_(None))

    # Validations
    @validates("name")
    def validate_name(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Name cannot be empty")
        if len(value) > 255:
            raise ValueError("Name is too long (maximum is 255 characters)")
        return value

    @validates("status")
    def validate_status(self, key: str, value: str) -> str:
        if value not in ("active", "inactive"):
            raise ValueError("Status must be 'active' or 'inactive'")
        return value

    # Methods
    def ancestors(self) -> list["Department"]:
        chain = []
        current = self.parent_department
        while current is not None:
            chain.append(current)
            current = current.parent_department
        chain.reverse()
        return chain


restrict_on_delete(Department, Department, Department.parent_department_id)
