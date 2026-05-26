import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, Integer, Index, Select, select
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base
from app.models.mixins import TenantMixin

if TYPE_CHECKING:
    from app.models.employee_custom_field_value import EmployeeCustomFieldValue


class EmployeeCustomFieldDefinition(TenantMixin, Base):
    __tablename__ = "employee_custom_field_definitions"

    FIELD_TYPES = ("text", "number", "date", "boolean", "select", "multi_select")

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    field_name: Mapped[str] = mapped_column(String(255), nullable=False)
    field_key: Mapped[str] = mapped_column(String(100), nullable=False)
    field_type: Mapped[str] = mapped_column(String(20), nullable=False)
    options: Mapped[list] = mapped_column(JSONB, nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    section: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    display_order: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    field_values: Mapped[list["EmployeeCustomFieldValue"]] = relationship("EmployeeCustomFieldValue", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_emp_custom_fields_tenant_key", "tenant_id", "field_key", unique=True),
        Index("index_employee_custom_field_definitions_on_tenant_id", "tenant_id"),
    )

    @classmethod
    def active(cls) -> Select:
        return select(cls).where(cls.is_active)

    @classmethod
    def ordered(cls) -> Select:
        return select(cls).order_by(cls.display_order)

    @validates("field_name")
    def validate_field_name(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Field name cannot be empty")
        if len(value) > 255:
            raise ValueError("Field name is too long (maximum is 255 characters)")
        return value

    @validates("field_key")
    def validate_field_key(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Field key cannot be empty")
        if len(value) > 100:
            raise ValueError("Field key is too long (maximum is 100 characters)")
        return value

    @validates("field_type")
    def validate_field_type(self, key: str, value: str) -> str:
        if value not in self.FIELD_TYPES:
            raise ValueError(f"Field type must be one of {self.FIELD_TYPES}")
        return value
