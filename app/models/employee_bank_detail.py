import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, Index, Select, select, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base
from app.models.mixins import TenantMixin

if TYPE_CHECKING:
    from app.models.employee import Employee


class EmployeeBankDetail(TenantMixin, Base):
    __tablename__ = "employee_bank_details"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    employee_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)

    bank_name: Mapped[str] = mapped_column(String(255), nullable=False)
    branch_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    account_number: Mapped[str] = mapped_column(String(50), nullable=False)
    ifsc_code: Mapped[str] = mapped_column(String(20), nullable=False)
    account_type: Mapped[str] = mapped_column(String(20), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    employee: Mapped["Employee"] = relationship("Employee")

    __table_args__ = (
        Index("idx_emp_bank_tenant_employee_account", "tenant_id", "employee_id", "account_number", unique=True),
        Index("index_employee_bank_details_on_employee_id", "employee_id"),
        Index("index_employee_bank_details_on_tenant_id", "tenant_id"),
    )

    @classmethod
    def active(cls) -> Select:
        return select(cls).where(cls.status == "active")

    @classmethod
    def primary(cls) -> Select:
        return select(cls).where(cls.is_primary)

    @validates("bank_name")
    def validate_bank_name(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Bank name cannot be empty")
        if len(value) > 255:
            raise ValueError("Bank name is too long (maximum is 255 characters)")
        return value

    @validates("account_number")
    def validate_account_number(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Account number cannot be empty")
        if len(value) > 50:
            raise ValueError("Account number is too long (maximum is 50 characters)")
        return value

    @validates("ifsc_code")
    def validate_ifsc_code(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("IFSC code cannot be empty")
        if len(value) > 20:
            raise ValueError("IFSC code is too long (maximum is 20 characters)")
        return value

    @validates("account_type")
    def validate_account_type(self, key: str, value: str) -> str:
        if value not in ("savings", "current"):
            raise ValueError("Account type must be 'savings' or 'current'")
        return value

    @validates("status")
    def validate_status(self, key: str, value: str) -> str:
        if value not in ("active", "inactive"):
            raise ValueError("Status must be 'active' or 'inactive'")
        return value
