import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, Integer, Index, Select, select, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base
from app.models.mixins import TenantMixin


if TYPE_CHECKING:
    from app.models.location import Location
    from app.models.holiday import Holiday


class HolidayCalendar(TenantMixin, Base):
    __tablename__ = "holiday_calendars"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    location_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("locations.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    location: Mapped[Optional["Location"]] = relationship("Location")
    holidays: Mapped[list["Holiday"]] = relationship("Holiday", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_holiday_calendars_unique", "tenant_id", "location_id", "year", unique=True),
        Index("index_holiday_calendars_on_location_id", "location_id"),
        Index("index_holiday_calendars_on_tenant_id", "tenant_id"),
    )

    @classmethod
    def active(cls) -> Select:
        return select(cls).where(cls.is_active)

    @classmethod
    def for_year(cls, year: int) -> Select:
        return select(cls).where(cls.year == year)

    @classmethod
    def for_location(cls, loc_id: uuid.UUID) -> Select:
        return select(cls).where(cls.location_id == loc_id)

    @classmethod
    def global_(cls) -> Select:
        return select(cls).where(cls.location_id.is_(None))

    @validates("name")
    def validate_name(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Name cannot be empty")
        if len(value) > 255:
            raise ValueError("Name is too long (maximum is 255 characters)")
        return value

    @validates("year")
    def validate_year(self, key: str, value: int) -> int:
        if value is None:
            raise ValueError("Year cannot be empty")
        return value
