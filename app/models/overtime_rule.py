import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Boolean, DateTime, Numeric, Index, Select, select
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base
from app.models.mixins import TenantMixin, AuditableMixin, restrict_on_delete


class OvertimeRule(TenantMixin, AuditableMixin, Base):
    __tablename__ = "overtime_rules"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    threshold_hours: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    rate_multiplier: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    max_daily_ot_hours: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), nullable=True)
    max_monthly_ot_hours: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    applicable_on_holidays: Mapped[bool] = mapped_column(Boolean, nullable=False)
    holiday_rate_multiplier: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    overtime_records: Mapped[list["OvertimeRecord"]] = relationship("OvertimeRecord")

    __table_args__ = (
        Index("index_overtime_rules_on_tenant_id_and_name", "tenant_id", "name", unique=True),
        Index("index_overtime_rules_on_tenant_id", "tenant_id"),
    )

    @classmethod
    def active(cls) -> Select:
        return select(cls).where(cls.is_active)

    @validates("name")
    def validate_name(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Name cannot be empty")
        if len(value) > 255:
            raise ValueError("Name is too long (maximum is 255 characters)")
        return value

    @validates("threshold_hours")
    def validate_threshold_hours(self, key: str, value: float) -> float:
        if value is None:
            raise ValueError("Threshold hours cannot be empty")
        if value <= 0:
            raise ValueError("Threshold hours must be greater than 0")
        return value

    @validates("rate_multiplier")
    def validate_rate_multiplier(self, key: str, value: float) -> float:
        if value is None:
            raise ValueError("Rate multiplier cannot be empty")
        if value <= 0:
            raise ValueError("Rate multiplier must be greater than 0")
        return value


from app.models.overtime_record import OvertimeRecord  # noqa: E402
restrict_on_delete(OvertimeRule, OvertimeRecord, OvertimeRecord.overtime_rule_id)  # noqa: E402
