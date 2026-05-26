import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.role import Role
    from app.models.user_role import UserRole
    from app.models.company import Company
    from app.models.location import Location
    from app.models.department import Department
    from app.models.employee import Employee


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    subdomain: Mapped[str] = mapped_column(String(100), nullable=False)
    domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(String, nullable=False)
    plan: Mapped[str] = mapped_column(String, nullable=False)
    settings: Mapped[dict] = mapped_column(JSONB, nullable=False)
    setup_completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    setup_steps: Mapped[dict] = mapped_column(JSONB, nullable=False)

    created_at: Mapped[object] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[object] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    users: Mapped[list["User"]] = relationship("User", cascade="all, delete-orphan")
    roles: Mapped[list["Role"]] = relationship("Role", cascade="all, delete-orphan")
    user_roles: Mapped[list["UserRole"]] = relationship("UserRole", cascade="all, delete-orphan")
    companies: Mapped[list["Company"]] = relationship("Company", cascade="all, delete-orphan")
    locations: Mapped[list["Location"]] = relationship("Location", cascade="all, delete-orphan")
    departments: Mapped[list["Department"]] = relationship("Department", cascade="all, delete-orphan")
    employees: Mapped[list["Employee"]] = relationship("Employee", cascade="all, delete-orphan")

    def active_or_trial(self) -> bool:
        return self.status in ("active", "trial")

    def setup_completed(self) -> bool:
        return self.setup_completed_at is not None

    @validates("name")
    def validate_name(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Name cannot be empty")
        if len(value) > 255:
            raise ValueError("Name is too long (maximum is 255 characters)")
        return value

    @validates("subdomain")
    def validate_subdomain(self, key: str, value: str) -> str:
        import re
        if not value or not value.strip():
            raise ValueError("Subdomain cannot be empty")
        if len(value) > 100:
            raise ValueError("Subdomain is too long (maximum is 100 characters)")
        if not re.match(r"\A[a-z0-9]([a-z0-9\-]*[a-z0-9])?\z", value):
            raise ValueError("Subdomain must be lowercase alphanumeric and hyphens only")
        return value

    @validates("domain")
    def validate_domain(self, key: str, value: Optional[str]) -> Optional[str]:
        if value is not None and len(value) > 255:
            raise ValueError("Domain is too long (maximum is 255 characters)")
        return value

    @validates("status")
    def validate_status(self, key: str, value: str) -> str:
        if not value:
            raise ValueError("Status cannot be empty")
        return value

    @validates("plan")
    def validate_plan(self, key: str, value: str) -> str:
        if not value:
            raise ValueError("Plan cannot be empty")
        return value


Index("index_tenants_on_subdomain", Tenant.subdomain, unique=True)

Index(
    "index_tenants_on_domain",
    Tenant.domain,
    unique=True,
    postgresql_where=(Tenant.domain.isnot(None)),
)

Index("index_tenants_on_status", Tenant.status)
