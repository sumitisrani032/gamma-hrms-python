import uuid
from datetime import datetime, date
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, Text, Integer, Date, Index, Select, select
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base
from app.models.mixins import TenantMixin

if TYPE_CHECKING:
    from app.models.wfh_request import WfhRequest


class WfhPolicy(TenantMixin, Base):
    __tablename__ = "wfh_policies"

    APPLICABLE_TO_OPTIONS = ("all", "department", "designation", "grade", "location")

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    requires_approval: Mapped[bool] = mapped_column(Boolean, nullable=False)
    max_wfh_per_month: Mapped[int] = mapped_column(Integer, nullable=False)
    min_days_advance: Mapped[int] = mapped_column(Integer, nullable=False)
    allowed_on_probation: Mapped[bool] = mapped_column(Boolean, nullable=False)
    allowed_days: Mapped[list] = mapped_column(JSONB, nullable=False)
    applicable_to: Mapped[str] = mapped_column(String(20), nullable=False)
    applicable_ids: Mapped[list] = mapped_column(JSONB, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False)
    effective_from: Mapped[datetime] = mapped_column(Date, nullable=False)
    effective_to: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    wfh_requests: Mapped[list["WfhRequest"]] = relationship("WfhRequest")

    __table_args__ = (
        Index("index_wfh_policies_on_tenant_id_and_is_active", "tenant_id", "is_active"),
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

    def applicable_to_employee(self, employee) -> bool:
        if self.applicable_to == "all":
            return True
        mapping = {
            "department": employee.department_id,
            "designation": employee.designation_id,
            "grade": employee.grade_id,
            "location": employee.location_id,
        }
        return mapping.get(self.applicable_to) in self.applicable_ids

    def allows_day(self, target_date: date) -> bool:
        if not self.allowed_days:
            return True
        day_name = target_date.strftime("%A").lower()
        return day_name in self.allowed_days

    @classmethod
    def resolve_for(cls, employee, target_date: date = None) -> Optional["WfhPolicy"]:
        if target_date is None:
            target_date = date.today()
        return None

    @validates("name")
    def validate_name(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Name cannot be empty")
        return value

    @validates("effective_from")
    def validate_effective_from(self, key: str, value: datetime) -> datetime:
        if value is None:
            raise ValueError("Effective from cannot be empty")
        return value

    @validates("applicable_to")
    def validate_applicable_to(self, key: str, value: str) -> str:
        if not value:
            raise ValueError("Applicable to cannot be empty")
        if value not in self.APPLICABLE_TO_OPTIONS:
            raise ValueError(f"Applicable to must be one of {self.APPLICABLE_TO_OPTIONS}")
        return value

    @validates("max_wfh_per_month")
    def validate_max_wfh_per_month(self, key: str, value: int) -> int:
        if value is not None and value < 0:
            raise ValueError("Max WFH per month must be greater than or equal to 0")
        return value

    @validates("min_days_advance")
    def validate_min_days_advance(self, key: str, value: int) -> int:
        if value is not None and value < 0:
            raise ValueError("Min days advance must be greater than or equal to 0")
        return value

    @validates("priority")
    def validate_priority(self, key: str, value: int) -> int:
        if value is not None and value < 0:
            raise ValueError("Priority must be greater than or equal to 0")
        return value
