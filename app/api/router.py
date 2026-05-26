from fastapi import APIRouter

from app.api.v1.api import api_router as v1_router
from app.core.config import settings

router = APIRouter()
router.include_router(v1_router, prefix=settings.API_V1_STR)

