from typing import Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db

security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
) -> dict[str, Any] | None:
    if credentials is None:
        return None

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY_BASE,
            algorithms=["HS256"],
        )
        return {
            "user_id": payload.get("user_id"),
            "tenant_id": payload.get("tenant_id"),
            "roles": payload.get("roles", []),
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


async def get_current_employee_id(
    db: AsyncSession = Depends(get_db),
    current_user: dict[str, Any] | None = Depends(get_current_user),
) -> str | None:
    if current_user is None:
        return None

    result = await db.execute(
        text("SELECT id FROM employees WHERE user_id = :user_id"),
        {"user_id": current_user["user_id"]},
    )
    row = result.fetchone()
    if row is None:
        return None
    return str(row[0])
