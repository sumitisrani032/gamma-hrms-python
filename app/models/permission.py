import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.role_permission import RolePermission
    from app.models.role import Role


class Permission(Base):
    __tablename__ = "permissions"

    SCOPES = ("global", "department", "team", "self")

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    resource: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    scope: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    role_permissions: Mapped[list["RolePermission"]] = relationship("RolePermission", cascade="all, delete-orphan")
    roles: Mapped[list["Role"]] = relationship("Role", secondary="role_permissions", viewonly=True)

    __table_args__ = (
        Index("index_permissions_on_resource_and_action_and_scope", "resource", "action", "scope", unique=True),
        Index("index_permissions_on_resource", "resource"),
    )

    @property
    def key(self) -> str:
        return f"{self.resource}:{self.action}:{self.scope}"

    @validates("resource")
    def validate_resource(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Resource cannot be empty")
        if len(value) > 100:
            raise ValueError("Resource is too long (maximum is 100 characters)")
        return value

    @validates("action")
    def validate_action(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Action cannot be empty")
        if len(value) > 50:
            raise ValueError("Action is too long (maximum is 50 characters)")
        return value

    @validates("scope")
    def validate_scope(self, key: str, value: str) -> str:
        if value not in self.SCOPES:
            raise ValueError(f"Scope must be one of {self.SCOPES}")
        return value
