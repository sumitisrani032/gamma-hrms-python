import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, Text, Date, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base
from app.models.mixins import TenantMixin


if TYPE_CHECKING:
    from app.models.holiday_calendar import HolidayCalendar


class Holiday(TenantMixin, Base):
    __tablename__ = "holidays"

    HOLIDAY_TYPES = ("mandatory", "optional", "restricted")

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    holiday_calendar_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("holiday_calendars.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[datetime] = mapped_column(Date, nullable=False)
    holiday_type: Mapped[str] = mapped_column(String(20), nullable=False)
    is_half_day: Mapped[bool] = mapped_column(Boolean, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    holiday_calendar: Mapped["HolidayCalendar"] = relationship("HolidayCalendar")

    __table_args__ = (
        Index("idx_holidays_unique", "tenant_id", "holiday_calendar_id", "date", unique=True),
        Index("index_holidays_on_holiday_calendar_id", "holiday_calendar_id"),
        Index("index_holidays_on_tenant_id", "tenant_id"),
    )

    @validates("name")
    def validate_name(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Name cannot be empty")
        if len(value) > 255:
            raise ValueError("Name is too long (maximum is 255 characters)")
        return value

    @validates("date")
    def validate_date(self, key: str, value: datetime) -> datetime:
        if value is None:
            raise ValueError("Date cannot be empty")
        return value

    @validates("holiday_type")
    def validate_holiday_type(self, key: str, value: str) -> str:
        if value not in self.HOLIDAY_TYPES:
            raise ValueError(f"Holiday type must be one of {self.HOLIDAY_TYPES}")
        return value
