import uuid
from datetime import datetime, date
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, DateTime, Text, Numeric, Date, Index, Select, select, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base
from app.models.mixins import TenantMixin

if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.user import User


class CompOffCredit(TenantMixin, Base):
    __tablename__ = "comp_off_credits"

    STATUSES = ["active", "used", "expired", "cancelled"]

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    earned_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    days_credited: Mapped[float] = mapped_column(Numeric(3, 1), nullable=False)
    days_used: Mapped[float] = mapped_column(Numeric(3, 1), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    approved_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", back_populates="comp_off_credits")
    approved_by: Mapped[Optional["User"]] = relationship("User")

    # Validators
    @validates("status")
    def validate_status(self, key, value):
        if value not in ("active", "used", "expired", "cancelled"):
            raise ValueError("status must be 'active', 'used', 'expired', or 'cancelled'")
        return value

    __table_args__ = (
        Index("idx_comp_off_credits_employee", "tenant_id", "employee_id"),
        Index("index_comp_off_credits_on_status", "status"),
        Index("index_comp_off_credits_on_expires_at", "expires_at"),
        Index("index_comp_off_credits_on_employee_id", "employee_id"),
        Index("index_comp_off_credits_on_tenant_id", "tenant_id"),
    )

    # Scopes
    @classmethod
    def active(cls) -> Select:
        return select(cls).where(cls.status == "active")

    @classmethod
    def not_expired(cls) -> Select:
        return select(cls).where(
            (cls.expires_at.is_(None)) | (cls.expires_at >= date.today())
        )

    @classmethod
    def available(cls) -> Select:
        return cls.active().not_expired().where(cls.days_credited > cls.days_used)

    # Methods
    def available_days(self) -> float:
        return self.days_credited - self.days_used
