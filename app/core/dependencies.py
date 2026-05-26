from typing import Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.rbac import has_permission
from app.core.security import get_current_user

__all__ = ["get_db", "require_permission"]


def require_permission(resource: str, action: str, required_scope: str | None = None):
    async def _check(
        current_user: dict[str, Any] | None = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> dict[str, Any]:
        if current_user is None:
            raise UnauthorizedException()

        if not await has_permission(db, current_user["roles"], resource, action, required_scope):
            raise ForbiddenException(detail=f"Missing permission: {resource}:{action}")

        return current_user

    return _check



