import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Text, Integer, Index, Select, select
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base
from app.models.mixins import TenantMixin, AuditableMixin, restrict_on_delete
from app.models.employee import Employee


class Grade(TenantMixin, AuditableMixin, Base):
    __tablename__ = "grades"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    employees: Mapped[list["Employee"]] = relationship("Employee")

    __table_args__ = (
        Index("index_grades_on_tenant_id_and_name", "tenant_id", "name", unique=True),
        Index("index_grades_on_tenant_id_and_rank", "tenant_id", "rank", unique=True),
        Index("index_grades_on_tenant_id", "tenant_id"),
    )

    @classmethod
    def active(cls) -> Select:
        return select(cls).where(cls.status == "active")

    @classmethod
    def ordered(cls) -> Select:
        return select(cls).order_by(cls.rank)

    @validates("name")
    def validate_name(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Name cannot be empty")
        if len(value) > 100:
            raise ValueError("Name is too long (maximum is 100 characters)")
        return value

    @validates("rank")
    def validate_rank(self, key: str, value: int) -> int:
        if value is None:
            raise ValueError("Rank cannot be empty")
        if value <= 0:
            raise ValueError("Rank must be greater than 0")
        return value

    @validates("status")
    def validate_status(self, key: str, value: str) -> str:
        if value not in ("active", "inactive"):
            raise ValueError("Status must be 'active' or 'inactive'")
        return value


restrict_on_delete(Grade, Employee, Employee.grade_id)
