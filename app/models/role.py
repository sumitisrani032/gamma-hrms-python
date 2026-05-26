import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, Text, Integer, Index, Select, select
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base
from app.models.mixins import TenantMixin

if TYPE_CHECKING:
    from app.models.role_permission import RolePermission
    from app.models.user_role import UserRole
    from app.models.permission import Permission
    from app.models.user import User


class Role(TenantMixin, Base):
    __tablename__ = "roles"

    MIN_RANK = 0
    MAX_RANK = 100

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_system_role: Mapped[bool] = mapped_column(Boolean, nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    role_permissions: Mapped[list["RolePermission"]] = relationship("RolePermission", cascade="all, delete-orphan")
    permissions: Mapped[list["Permission"]] = relationship("Permission", secondary="role_permissions", viewonly=True)

    user_roles: Mapped[list["UserRole"]] = relationship("UserRole", cascade="all, delete-orphan")
    users: Mapped[list["User"]] = relationship("User", secondary="user_roles", viewonly=True)

    __table_args__ = (
        Index("index_roles_on_tenant_id_and_name", "tenant_id", "name", unique=True),
        Index("index_roles_on_tenant_id_and_rank", "tenant_id", "rank"),
    )

    @classmethod
    def system_roles(cls) -> Select:
        return select(cls).where(cls.is_system_role)

    @property
    def tier_label(self) -> str:
        return f"Tier-{self.rank}"

    def system_role(self) -> bool:
        return self.is_system_role

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
        if not isinstance(value, int) or value < self.MIN_RANK or value > self.MAX_RANK:
            raise ValueError(f"Rank must be an integer between {self.MIN_RANK} and {self.MAX_RANK}")
        return value
