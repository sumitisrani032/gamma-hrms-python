import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base
from app.models.mixins import TenantMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.role import Role


class UserRole(TenantMixin, Base):
    __tablename__ = "user_roles"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    role_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    user: Mapped["User"] = relationship("User")
    role: Mapped["Role"] = relationship("Role")

    __table_args__ = (
        Index("index_user_roles_on_user_id_and_role_id", "user_id", "role_id", unique=True),
        Index("index_user_roles_on_user_id", "user_id"),
        Index("index_user_roles_on_role_id", "role_id"),
    )

    @validates("role_id")
    def validate_role_id(self, key: str, value: uuid.UUID) -> uuid.UUID:
        if value is None:
            raise ValueError("Role cannot be empty")
        return value
