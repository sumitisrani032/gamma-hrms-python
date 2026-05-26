from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

SCOPE_HIERARCHY = ["global", "department", "team", "self"]


async def has_permission(
    db: AsyncSession,
    roles: list[str],
    resource: str,
    action: str,
    required_scope: str | None = None,
) -> bool:
    if not roles:
        return False

    result = await db.execute(
        text("""
            SELECT p.scope FROM role_permissions rp
            INNER JOIN roles r ON r.id = rp.role_id
            INNER JOIN permissions p ON p.id = rp.permission_id
            WHERE r.name = ANY(:roles)
            AND p.resource = :resource
            AND p.action = :action
        """),
        {
            "roles": roles,
            "resource": resource,
            "action": action,
        },
    )
    scopes = [row[0] for row in result.fetchall()]

    if not scopes:
        return False

    if required_scope is None:
        return True

    if required_scope not in SCOPE_HIERARCHY:
        return False

    required_idx = SCOPE_HIERARCHY.index(required_scope)

    for scope in scopes:
        if scope in SCOPE_HIERARCHY:
            granted_idx = SCOPE_HIERARCHY.index(scope)
            if granted_idx <= required_idx:
                return True

    return False


async def get_highest_scope(
    db: AsyncSession,
    roles: list[str],
    resource: str,
    action: str,
) -> str | None:
    if not roles:
        return None

    result = await db.execute(
        text("""
            SELECT p.scope FROM role_permissions rp
            INNER JOIN roles r ON r.id = rp.role_id
            INNER JOIN permissions p ON p.id = rp.permission_id
            WHERE r.name = ANY(:roles)
            AND p.resource = :resource
            AND p.action = :action
        """),
        {
            "roles": roles,
            "resource": resource,
            "action": action,
        },
    )
    scopes = {row[0] for row in result.fetchall()}

    for scope in SCOPE_HIERARCHY:
        if scope in scopes:
            return scope

    return None
