"""FastAPI middleware that populates Current from the incoming request.

Rails equivalent: This is the "request lifecycle" glue that Rails provides
out of the box via its middleware stack. In Rails, CurrentAttributes are
automatically cleared after each request. Here we also:

1. Extract basic request metadata (ip_address, user_agent).
2. (Planned) Authenticate the user via JWT and set ``Current.user``.
3. (Planned) Resolve the tenant from the request subdomain / header and
   set ``Current.tenant``, then sync to PostgreSQL with
   ``SET app.current_tenant_id``.
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.models.current import Current


class CurrentContextMiddleware(BaseHTTPMiddleware):
    """Middleware that initialises and clears Current for each request.

    Register this middleware **after** CORSMiddleware but **before** your
    router in ``main.py``:

    .. code-block:: python

        app.add_middleware(CurrentContextMiddleware)
        app.include_router(api_router, ...)
    """

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        # --- Initialise context for this request ---
        Current.reset()
        Current.ip_address = request.client.host if request.client else None
        Current.user_agent = request.headers.get("user-agent")

        # === TODO: Authenticate user from JWT =========================
        # Current.user = await get_current_user_from_request(request)

        # === TODO: Resolve tenant from subdomain / header ============
        # tenant = await resolve_tenant_from_request(request)
        # if tenant:
        #     Current.tenant = tenant
        #     await sync_tenant_to_db(tenant)

        # --- Dispatch to handler ---
        response = await call_next(request)

        # --- Cleanup after request ---
        Current.reset()
        return response
