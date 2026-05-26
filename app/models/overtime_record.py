import uuid
from datetime import datetime, date
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, Numeric, Date, Index, Select, select, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base
from app.models.mixins import TenantMixin


if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.overtime_rule import OvertimeRule
    from app.models.user import User


class OvertimeRecord(TenantMixin, Base):
    __tablename__ = "overtime_records"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    employee_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    overtime_rule_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("overtime_rules.id"), nullable=False)
    date: Mapped[datetime] = mapped_column(Date, nullable=False)
    overtime_hours: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    rate_multiplier: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    is_holiday_ot: Mapped[bool] = mapped_column(Boolean, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    approved_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    employee: Mapped["Employee"] = relationship("Employee")
    overtime_rule: Mapped["OvertimeRule"] = relationship("OvertimeRule")
    approved_by: Mapped[Optional["User"]] = relationship("User")

    __table_args__ = (
        Index("idx_overtime_records_unique", "tenant_id", "employee_id", "date", unique=True),
        Index("index_overtime_records_on_employee_id", "employee_id"),
        Index("index_overtime_records_on_overtime_rule_id", "overtime_rule_id"),
        Index("index_overtime_records_on_status", "status"),
        Index("index_overtime_records_on_tenant_id", "tenant_id"),
    )

    @classmethod
    def for_month(cls, year: int, month: int) -> Select:
        import calendar
        start = date(year, month, 1)
        end = date(year, month, calendar.monthrange(year, month)[1])
        return select(cls).where(cls.date.between(start, end))

    @validates("date")
    def validate_date(self, key: str, value: datetime) -> datetime:
        if value is None:
            raise ValueError("Date cannot be empty")
        return value

    @validates("overtime_hours")
    def validate_overtime_hours(self, key: str, value: float) -> float:
        if value is None:
            raise ValueError("Overtime hours cannot be empty")
        if value <= 0:
            raise ValueError("Overtime hours must be greater than 0")
        return value

    @validates("rate_multiplier")
    def validate_rate_multiplier(self, key: str, value: float) -> float:
        if value is None:
            raise ValueError("Rate multiplier cannot be empty")
        if value <= 0:
            raise ValueError("Rate multiplier must be greater than 0")
        return value

    @validates("status")
    def validate_status(self, key: str, value: str) -> str:
        if value not in ("computed", "approved", "rejected"):
            raise ValueError("Status must be 'computed', 'approved', or 'rejected'")
        return value
