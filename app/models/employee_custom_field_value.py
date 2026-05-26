import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import DateTime, Text, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TenantMixin


if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.employee_custom_field_definition import EmployeeCustomFieldDefinition


class EmployeeCustomFieldValue(TenantMixin, Base):
    __tablename__ = "employee_custom_field_values"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    employee_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    field_definition_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("employee_custom_field_definitions.id"), nullable=False)
    value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    employee: Mapped["Employee"] = relationship("Employee")
    field_definition: Mapped["EmployeeCustomFieldDefinition"] = relationship("EmployeeCustomFieldDefinition")

    __table_args__ = (
        Index("idx_emp_custom_values_unique", "tenant_id", "employee_id", "field_definition_id", unique=True),
        Index("index_employee_custom_field_values_on_employee_id", "employee_id"),
        Index("index_employee_custom_field_values_on_field_definition_id", "field_definition_id"),
        Index("index_employee_custom_field_values_on_tenant_id", "tenant_id"),
    )
