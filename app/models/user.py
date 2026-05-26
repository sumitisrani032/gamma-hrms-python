import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base
from app.models.mixins import TenantMixin

if TYPE_CHECKING:
    from app.models.refresh_token import RefreshToken
    from app.models.user_role import UserRole
    from app.models.role import Role
    from app.models.employee import Employee


class User(TenantMixin, Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_digest: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False)
    mfa_secret: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship("RefreshToken", cascade="all, delete-orphan")
    user_roles: Mapped[list["UserRole"]] = relationship("UserRole", cascade="all, delete-orphan")
    roles: Mapped[list["Role"]] = relationship("Role", secondary="user_roles", viewonly=True)
    employee: Mapped[Optional["Employee"]] = relationship("Employee", uselist=False)

    __table_args__ = (
        Index("index_users_on_tenant_id_and_email", "tenant_id", "email", unique=True),
        Index("index_users_on_status", "status"),
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def active_for_auth(self) -> bool:
        return self.status == "active"

    @property
    def role_names(self) -> list[str]:
        return [r.name for r in self.roles]

    def has_role(self, role_name: str) -> bool:
        return role_name in self.role_names

    def downcase_email(self) -> None:
        if self.email:
            self.email = self.email.lower()

    @validates("email")
    def validate_email(self, key: str, value: str) -> str:
        import re
        if not value or not value.strip():
            raise ValueError("Email cannot be empty")
        if not re.match(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
            raise ValueError("Email is invalid")
        return value

    @validates("first_name")
    def validate_first_name(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("First name cannot be empty")
        if len(value) > 100:
            raise ValueError("First name is too long (maximum is 100 characters)")
        return value

    @validates("last_name")
    def validate_last_name(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Last name cannot be empty")
        if len(value) > 100:
            raise ValueError("Last name is too long (maximum is 100 characters)")
        return value

    @validates("status")
    def validate_status(self, key: str, value: str) -> str:
        if not value:
            raise ValueError("Status cannot be empty")
        return value
