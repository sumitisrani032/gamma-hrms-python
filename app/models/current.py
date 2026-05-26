from contextvars import ContextVar
from sqlalchemy import create_engine, text


_ATTRS = ("tenant", "user", "ip_address", "user_agent")
_sync_engine = None


def _get_sync_engine():
    from app.core.config import settings
    global _sync_engine
    if _sync_engine is None:
        sync_url = str(settings.DATABASE_URL).replace("+asyncpg", "")
        _sync_engine = create_engine(sync_url, pool_pre_ping=True)
    return _sync_engine


class CurrentMeta(type):
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        cls._vars = {a: ContextVar(f"current_{a}", default=None) for a in _ATTRS}
        return cls

    def __getattr__(cls, name):
        _vars = cls.__dict__.get("_vars", {})
        if name in _vars:
            return _vars[name].get()
        raise AttributeError(name)

    def __setattr__(cls, name, value):
        _vars = cls.__dict__.get("_vars", {})
        if name in _vars:
            _vars[name].set(value)
            if name == "tenant":
                cls._sync_tenant_to_database(value)
        else:
            super().__setattr__(name, value)

    def __delattr__(cls, name):
        _vars = cls.__dict__.get("_vars", {})
        if name in _vars:
            _vars[name].set(None)
        else:
            super().__delattr__(name)


class Current(metaclass=CurrentMeta):
    @classmethod
    def _sync_tenant_to_database(cls, tenant) -> None:
        try:
            engine = _get_sync_engine()
            with engine.connect() as conn:
                if tenant is None:
                    conn.execute(text("RESET app.current_tenant_id"))
                else:
                    conn.execute(
                        text("SELECT set_config('app.current_tenant_id', :val, true)"),
                        {"val": str(tenant.id)},
                    )
                conn.commit()
        except Exception:
            pass

    @classmethod
    def reset(cls) -> None:
        _vars = cls.__dict__.get("_vars", {})
        for var in _vars.values():
            var.set(None)
