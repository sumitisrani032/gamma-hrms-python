from fastapi import APIRouter

from app.api.v1.endpoints import health, payroll

api_router = APIRouter()

# Include health router
api_router.include_router(health.router, tags=["health"])
api_router.include_router(payroll.router)
