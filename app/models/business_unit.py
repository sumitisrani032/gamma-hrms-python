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


class BusinessUnit(TenantMixin, AuditableMixin, Base):
    __tablename__ = "business_units"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    head_employee_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="business_units")
    head_employee: Mapped[Optional["Employee"]] = relationship("Employee", foreign_keys=[head_employee_id])
    employees: Mapped[list["Employee"]] = relationship("Employee", back_populates="business_unit")

    # Validators
    @validates("status")
    def validate_status(self, key, value):
        if value not in ("active", "inactive"):
            raise ValueError("status must be 'active' or 'inactive'")
        return value

    __table_args__ = (
        Index("index_business_units_on_tenant_id_and_name", "tenant_id", "name", unique=True),
        Index("index_business_units_on_company_id", "company_id"),
        Index("index_business_units_on_tenant_id", "tenant_id"),
    )

    # Scopes
    @classmethod
    def active(cls) -> Select:
        return select(cls).where(cls.status == "active")


from app.models.employee import Employee  # noqa: E402
restrict_on_delete(BusinessUnit, Employee, Employee.business_unit_id)  # noqa: E402
