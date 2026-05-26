import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, Numeric, Index, Select, select, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates, object_session

from app.db.base import Base
from app.models.mixins import TenantMixin

if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.leave_type import LeaveType


class LeaveBalance(TenantMixin, Base):
    __tablename__ = "leave_balances"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    employee_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    leave_type_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("leave_types.id"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    entitled: Mapped[float] = mapped_column(Numeric(5, 1), nullable=False)
    accrued: Mapped[float] = mapped_column(Numeric(5, 1), nullable=False)
    used: Mapped[float] = mapped_column(Numeric(5, 1), nullable=False)
    carry_forwarded: Mapped[float] = mapped_column(Numeric(5, 1), nullable=False)
    adjusted: Mapped[float] = mapped_column(Numeric(5, 1), nullable=False)
    balance: Mapped[float] = mapped_column(Numeric(5, 1), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    employee: Mapped["Employee"] = relationship("Employee")
    leave_type: Mapped["LeaveType"] = relationship("LeaveType")

    __table_args__ = (
        Index("idx_leave_balances_unique", "tenant_id", "employee_id", "leave_type_id", "year", unique=True),
        Index("index_leave_balances_on_employee_id", "employee_id"),
        Index("index_leave_balances_on_leave_type_id", "leave_type_id"),
        Index("index_leave_balances_on_tenant_id", "tenant_id"),
    )

    @classmethod
    def for_year(cls, year: int) -> Select:
        return select(cls).where(cls.year == year)

    @classmethod
    def for_type(cls, type_id: uuid.UUID) -> Select:
        return select(cls).where(cls.leave_type_id == type_id)

    @validates("year")
    def validate_year(self, key: str, value: int) -> int:
        if value is None:
            raise ValueError("Year cannot be empty")
        return value

    def recalculate(self) -> None:
        self.balance = self.carry_forwarded + self.accrued - self.used + self.adjusted
        object_session(self).flush()

    def available(self) -> float:
        return self.carry_forwarded + self.accrued - self.used + self.adjusted
