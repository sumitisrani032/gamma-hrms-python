import uuid
from datetime import datetime, date
from typing import Optional, TYPE_CHECKING

from sqlalchemy import DateTime, Date, Index, Select, select
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base
from app.models.mixins import TenantMixin

if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.shift import Shift
    from app.models.user import User


class ShiftAssignment(TenantMixin, Base):
    __tablename__ = "shift_assignments"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    employee_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    shift_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    effective_from: Mapped[datetime] = mapped_column(Date, nullable=False)
    effective_to: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    assigned_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    employee: Mapped["Employee"] = relationship("Employee")
    shift: Mapped["Shift"] = relationship("Shift")
    assigned_by: Mapped[Optional["User"]] = relationship("User")

    __table_args__ = (
        Index("idx_shift_assignments_unique", "tenant_id", "employee_id", "effective_from"),
        Index("index_shift_assignments_on_employee_id", "employee_id"),
        Index("index_shift_assignments_on_shift_id", "shift_id"),
    )

    @classmethod
    def active_on(cls, target_date: date) -> Select:
        return select(cls).where(
            cls.effective_from <= target_date,
            (cls.effective_to.is_(None)) | (cls.effective_to >= target_date),
        )

    @classmethod
    def current(cls) -> Select:
        return cls.active_on(date.today())

    @validates("effective_from")
    def validate_effective_from(self, key: str, value: datetime) -> datetime:
        if value is None:
            raise ValueError("Effective from cannot be empty")
        return value
