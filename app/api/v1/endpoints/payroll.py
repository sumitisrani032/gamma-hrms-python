from fastapi import APIRouter

from app.modules.payroll.router import router as payroll_module_router

router = APIRouter(prefix="/payroll")
router.include_router(payroll_module_router)
