from sqlalchemy import text

from app.db.session import get_db, AsyncSessionLocal
from app.models.current import Current


async def get_current_tenant():
    """Dependency that returns the tenant set by CurrentContextMiddleware."""
    return Current.tenant


async def get_current_user():
    """Dependency that returns the user set by CurrentContextMiddleware."""
    return Current.user


async def sync_tenant_to_db(tenant) -> None:
    """Sync ``Current.tenant`` to the PostgreSQL session variable used by RLS.

    Mirrors the ``sync_tenant_to_database`` method in Rails' ``current.rb``.
    """
    if tenant is None:
        async with AsyncSessionLocal() as session:
            await session.execute(text("RESET app.current_tenant_id"))
            await session.commit()
    else:
        async with AsyncSessionLocal() as session:
            await session.execute(
                text("SELECT set_config('app.current_tenant_id', :val, true)"),
                {"val": str(tenant.id)},
            )
            await session.commit()


__all__ = [
    "get_db",
    "get_current_tenant",
    "get_current_user",
    "sync_tenant_to_db",
]
