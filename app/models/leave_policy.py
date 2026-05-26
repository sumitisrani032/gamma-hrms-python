import uuid
from datetime import datetime, date
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, Numeric, Integer, Date, Index, Select, select, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base
from app.models.mixins import TenantMixin, AuditableMixin


if TYPE_CHECKING:
    from app.models.leave_type import LeaveType


class LeavePolicy(TenantMixin, AuditableMixin, Base):
    __tablename__ = "leave_policies"

    ACCRUAL_TYPES = ("annual", "monthly", "quarterly")
    PRORATION_BASES = ("calendar_days", "working_days", "15th_cutoff")
    APPLICABLE_TO_OPTIONS = ("all", "grade", "department", "designation", "location")

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    leave_type_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("leave_types.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    effective_from: Mapped[datetime] = mapped_column(Date, nullable=False)
    effective_to: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    accrual_type: Mapped[str] = mapped_column(String(20), nullable=False)
    annual_quota: Mapped[float] = mapped_column(Numeric(5, 1), nullable=False)
    monthly_accrual: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    prorate_on_joining: Mapped[bool] = mapped_column(Boolean, nullable=False)
    prorate_on_exit: Mapped[bool] = mapped_column(Boolean, nullable=False)
    proration_basis: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    applicable_to: Mapped[str] = mapped_column(String(20), nullable=False)
    applicable_ids: Mapped[list] = mapped_column(JSONB, nullable=False)
    min_days_per_request: Mapped[Optional[float]] = mapped_column(Numeric(3, 1), nullable=True)
    max_days_per_request: Mapped[Optional[float]] = mapped_column(Numeric(5, 1), nullable=True)
    requires_approval: Mapped[bool] = mapped_column(Boolean, nullable=False)
    advance_days_required: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    leave_type: Mapped["LeaveType"] = relationship("LeaveType")

    __table_args__ = (
        Index("idx_leave_policies_unique", "tenant_id", "leave_type_id", "name", unique=True),
        Index("index_leave_policies_on_leave_type_id", "leave_type_id"),
        Index("index_leave_policies_on_tenant_id", "tenant_id"),
    )

    @classmethod
    def active(cls) -> Select:
        return select(cls).where(cls.is_active)

    @classmethod
    def effective_on(cls, target_date: date) -> Select:
        return select(cls).where(
            cls.effective_from <= target_date,
            (cls.effective_to.is_(None)) | (cls.effective_to >= target_date),
        )

    @validates("name")
    def validate_name(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Name cannot be empty")
        if len(value) > 255:
            raise ValueError("Name is too long (maximum is 255 characters)")
        return value

    @validates("effective_from")
    def validate_effective_from(self, key: str, value: datetime) -> datetime:
        if value is None:
            raise ValueError("Effective from cannot be empty")
        return value

    @validates("accrual_type")
    def validate_accrual_type(self, key: str, value: str) -> str:
        if value not in self.ACCRUAL_TYPES:
            raise ValueError(f"Accrual type must be one of {self.ACCRUAL_TYPES}")
        return value

    @validates("annual_quota")
    def validate_annual_quota(self, key: str, value: float) -> float:
        if value is None:
            raise ValueError("Annual quota cannot be empty")
        if value < 0:
            raise ValueError("Annual quota must be greater than or equal to 0")
        return value

    @validates("applicable_to")
    def validate_applicable_to(self, key: str, value: str) -> str:
        if value not in self.APPLICABLE_TO_OPTIONS:
            raise ValueError(f"Applicable to must be one of {self.APPLICABLE_TO_OPTIONS}")
        return value

    def applicable_to_employee(self, employee) -> bool:
        if self.applicable_to == "all":
            return True
        mapping = {
            "grade": employee.grade_id,
            "department": employee.department_id,
            "designation": employee.designation_id,
            "location": employee.location_id,
        }
        return mapping.get(self.applicable_to) in self.applicable_ids
