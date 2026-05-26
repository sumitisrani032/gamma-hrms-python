import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, Text, Date, Index, Select, select
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base
from app.models.mixins import TenantMixin, AuditableMixin, restrict_on_delete

if TYPE_CHECKING:
    from app.models.department import Department
    from app.models.business_unit import BusinessUnit
    from app.models.employee import Employee


class Company(TenantMixin, AuditableMixin, Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    legal_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    registration_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tax_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    incorporation_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    pincode: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    departments: Mapped[list["Department"]] = relationship("Department", back_populates="company")
    business_units: Mapped[list["BusinessUnit"]] = relationship("BusinessUnit", back_populates="company")
    employees: Mapped[list["Employee"]] = relationship("Employee", back_populates="company")

    # Validators
    @validates("status")
    def validate_status(self, key, value):
        if value not in ("active", "inactive"):
            raise ValueError("status must be 'active' or 'inactive'")
        return value

    __table_args__ = (
        Index("index_companies_on_tenant_id_and_name", "tenant_id", "name", unique=True),
        Index("index_companies_on_tenant_id", "tenant_id"),
    )

    # Scopes
    @classmethod
    def active(cls) -> Select:
        return select(cls).where(cls.status == "active")

    # Methods
    def primary(self) -> bool:
        return self.is_primary


from app.models.department import Department  # noqa: E402
from app.models.business_unit import BusinessUnit  # noqa: E402
from app.models.employee import Employee  # noqa: E402
restrict_on_delete(Company, Department, Department.company_id)  # noqa: E402
restrict_on_delete(Company, BusinessUnit, BusinessUnit.company_id)  # noqa: E402
restrict_on_delete(Company, Employee, Employee.company_id)  # noqa: E402
