import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, DateTime, Text, Date, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TenantMixin


if TYPE_CHECKING:
    from app.models.employee import Employee


class EmployeePersonalDetail(TenantMixin, Base):
    __tablename__ = "employee_personal_details"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    employee_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)

    current_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    current_city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    current_state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    current_country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    current_pincode: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    permanent_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    permanent_city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    permanent_state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    permanent_country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    permanent_pincode: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    emergency_contact_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    emergency_contact_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    emergency_contact_relation: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    pan_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    aadhaar_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    passport_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    passport_expiry: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    uan_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    employee: Mapped["Employee"] = relationship("Employee")

    __table_args__ = (
        Index("idx_emp_personal_details_tenant_employee", "tenant_id", "employee_id", unique=True),
        Index("index_employee_personal_details_on_employee_id", "employee_id"),
        Index("index_employee_personal_details_on_tenant_id", "tenant_id"),
    )
