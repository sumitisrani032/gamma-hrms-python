import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, Text, Numeric, Index, Select, select
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base
from app.models.mixins import TenantMixin, AuditableMixin, restrict_on_delete


if TYPE_CHECKING:
    from app.models.holiday_calendar import HolidayCalendar


class Location(TenantMixin, AuditableMixin, Base):
    __tablename__ = "locations"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    pincode: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), nullable=False)
    latitude: Mapped[Optional[float]] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Numeric(10, 7), nullable=True)
    is_headquarters: Mapped[bool] = mapped_column(Boolean, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    employees: Mapped[list["Employee"]] = relationship("Employee")
    holiday_calendars: Mapped[list["HolidayCalendar"]] = relationship("HolidayCalendar", cascade="all, delete-orphan")

    __table_args__ = (
        Index("index_locations_on_tenant_id_and_name", "tenant_id", "name", unique=True),
        Index("index_locations_on_tenant_id", "tenant_id"),
    )

    @classmethod
    def active(cls) -> Select:
        return select(cls).where(cls.status == "active")

    @validates("name")
    def validate_name(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Name cannot be empty")
        if len(value) > 255:
            raise ValueError("Name is too long (maximum is 255 characters)")
        return value

    @validates("country")
    def validate_country(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Country cannot be empty")
        return value

    @validates("timezone")
    def validate_timezone(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Timezone cannot be empty")
        return value

    @validates("status")
    def validate_status(self, key: str, value: str) -> str:
        if value not in ("active", "inactive"):
            raise ValueError("Status must be 'active' or 'inactive'")
        return value


from app.models.employee import Employee  # noqa: E402
restrict_on_delete(Location, Employee, Employee.location_id)  # noqa: E402
