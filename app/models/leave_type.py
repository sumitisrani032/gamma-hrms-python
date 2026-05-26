import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, Text, Integer, Numeric, Index, Select, select
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base
from app.models.mixins import TenantMixin, AuditableMixin, restrict_on_delete


if TYPE_CHECKING:
    from app.models.leave_policy import LeavePolicy
    from app.models.leave_balance import LeaveBalance
    from app.models.leave_request import LeaveRequest


class LeaveType(TenantMixin, AuditableMixin, Base):
    __tablename__ = "leave_types"

    BACKDATED_ALLOWED_CODES = ("SL", "ML", "PL")

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_paid: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_carry_forward: Mapped[bool] = mapped_column(Boolean, nullable=False)
    max_carry_forward_days: Mapped[Optional[float]] = mapped_column(Numeric(5, 1), nullable=True)
    is_encashable: Mapped[bool] = mapped_column(Boolean, nullable=False)
    max_encashment_days: Mapped[Optional[float]] = mapped_column(Numeric(5, 1), nullable=True)
    is_half_day_allowed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_negative_balance_allowed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    max_negative_days: Mapped[Optional[float]] = mapped_column(Numeric(5, 1), nullable=True)
    requires_attachment: Mapped[bool] = mapped_column(Boolean, nullable=False)
    min_days_before_application: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_consecutive_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gender_applicable: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    color_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    leave_policies: Mapped[list["LeavePolicy"]] = relationship("LeavePolicy", cascade="all, delete-orphan")
    leave_balances: Mapped[list["LeaveBalance"]] = relationship("LeaveBalance", cascade="all, delete-orphan")
    leave_requests: Mapped[list["LeaveRequest"]] = relationship("LeaveRequest")

    __table_args__ = (
        Index("index_leave_types_on_tenant_id_and_code", "tenant_id", "code", unique=True),
        Index("index_leave_types_on_tenant_id_and_name", "tenant_id", "name", unique=True),
        Index("index_leave_types_on_tenant_id", "tenant_id"),
    )

    @classmethod
    def active(cls) -> Select:
        return select(cls).where(cls.is_active)

    @validates("name")
    def validate_name(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Name cannot be empty")
        if len(value) > 100:
            raise ValueError("Name is too long (maximum is 100 characters)")
        return value

    @validates("code")
    def validate_code(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Code cannot be empty")
        if len(value) > 20:
            raise ValueError("Code is too long (maximum is 20 characters)")
        return value

    def allow_backdated_application(self) -> bool:
        return self.code.upper() in self.BACKDATED_ALLOWED_CODES


from app.models.leave_request import LeaveRequest  # noqa: E402
restrict_on_delete(LeaveType, LeaveRequest, LeaveRequest.leave_type_id)  # noqa: E402
