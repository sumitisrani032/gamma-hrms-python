from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Any

from app.core.dependencies import get_db, require_permission
from app.core.rbac import has_permission
from app.core.security import get_current_employee_id, get_current_user
from app.modules.payroll.schema import (
    EmployeePayslipCreate,
    EmployeePayslipGenerateRequest,
    EmployeePayslipGenerateResult,
    EmployeePayslipList,
    EmployeePayslipRead,
    EmployeePayslipUpdate,
    EmployeeSalaryComponentCreate,
    EmployeeSalaryComponentList,
    EmployeeSalaryComponentRead,
    EmployeeSalaryComponentUpdate,
    EmployeeSalaryCreate,
    EmployeeSalaryList,
    EmployeeSalaryRead,
    EmployeeSalaryUpdate,
    SalaryComponentCreate,
    SalaryComponentList,
    SalaryComponentRead,
    SalaryComponentUpdate,
)
from app.modules.payroll.service import (
    EmployeePayslipService,
    EmployeeSalaryComponentService,
    EmployeeSalaryService,
    SalaryComponentService,
)

router = APIRouter(tags=["payroll"])


# ──────────────────────────────────────────────
# Dependency helpers
# ──────────────────────────────────────────────
def _salary_component_service(db: AsyncSession = Depends(get_db)) -> SalaryComponentService:
    return SalaryComponentService(db)


def _employee_salary_service(db: AsyncSession = Depends(get_db)) -> EmployeeSalaryService:
    return EmployeeSalaryService(db)


def _employee_salary_component_service(
    db: AsyncSession = Depends(get_db),
) -> EmployeeSalaryComponentService:
    return EmployeeSalaryComponentService(db)


def _employee_payslip_service(db: AsyncSession = Depends(get_db)) -> EmployeePayslipService:
    return EmployeePayslipService(db)


# ──────────────────────────────────────────────
# Permission presets
# ──────────────────────────────────────────────
_process_perm = Depends(require_permission("payroll", "process"))
_read_perm = Depends(require_permission("payroll", "read"))


async def _can_view_draft(
    current_user: dict[str, Any] | None = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> bool:
    if current_user is None:
        return False
    return await has_permission(db, current_user["roles"], "payroll", "process")


# ══════════════════════════════════════════════
# Salary Components
# ══════════════════════════════════════════════
salary_component_router = APIRouter(prefix="/salary-components", dependencies=[_read_perm])


@salary_component_router.post("", response_model=SalaryComponentRead, status_code=status.HTTP_201_CREATED, dependencies=[_process_perm])
async def create_salary_component(
    payload: SalaryComponentCreate,
    service: SalaryComponentService = Depends(_salary_component_service),
    employee_id: str | None = Depends(get_current_employee_id),
) -> SalaryComponentRead:
    return await service.create(payload, employee_id=employee_id)


@salary_component_router.get("", response_model=SalaryComponentList)
async def list_salary_components(
    is_active: bool | None = None,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    service: SalaryComponentService = Depends(_salary_component_service),
) -> SalaryComponentList:
    return await service.list(is_active=is_active, offset=offset, limit=limit)


@salary_component_router.get("/{component_id}", response_model=SalaryComponentRead)
async def get_salary_component(
    component_id: int,
    service: SalaryComponentService = Depends(_salary_component_service),
) -> SalaryComponentRead:
    return await service.get(component_id)


@salary_component_router.patch("/{component_id}", response_model=SalaryComponentRead, dependencies=[_process_perm])
async def update_salary_component(
    component_id: int,
    payload: SalaryComponentUpdate,
    service: SalaryComponentService = Depends(_salary_component_service),
) -> SalaryComponentRead:
    return await service.update(component_id, payload)


@salary_component_router.delete("/{component_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[_process_perm])
async def delete_salary_component(
    component_id: int,
    service: SalaryComponentService = Depends(_salary_component_service),
) -> Response:
    await service.delete(component_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ══════════════════════════════════════════════
# Employee Salaries
# ══════════════════════════════════════════════
employee_salary_router = APIRouter(prefix="/employee-salaries", dependencies=[_read_perm])


@employee_salary_router.post("", response_model=EmployeeSalaryRead, status_code=status.HTTP_201_CREATED, dependencies=[_process_perm])
async def create_employee_salary(
    payload: EmployeeSalaryCreate,
    service: EmployeeSalaryService = Depends(_employee_salary_service),
    employee_id: str | None = Depends(get_current_employee_id),
) -> EmployeeSalaryRead:
    return await service.create(payload, employee_id=employee_id)


@employee_salary_router.get("", response_model=EmployeeSalaryList)
async def list_employee_salaries(
    employee_id: str | None = None,
    search: str | None = None,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    service: EmployeeSalaryService = Depends(_employee_salary_service),
) -> EmployeeSalaryList:
    return await service.list(employee_id=employee_id, search=search, offset=offset, limit=limit)


@employee_salary_router.get("/{salary_id}", response_model=EmployeeSalaryRead)
async def get_employee_salary(
    salary_id: int,
    service: EmployeeSalaryService = Depends(_employee_salary_service),
) -> EmployeeSalaryRead:
    return await service.get(salary_id)


@employee_salary_router.patch("/{salary_id}", response_model=EmployeeSalaryRead, dependencies=[_process_perm])
async def update_employee_salary(
    salary_id: int,
    payload: EmployeeSalaryUpdate,
    service: EmployeeSalaryService = Depends(_employee_salary_service),
) -> EmployeeSalaryRead:
    return await service.update(salary_id, payload)


@employee_salary_router.delete("/{salary_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[_process_perm])
async def delete_employee_salary(
    salary_id: int,
    service: EmployeeSalaryService = Depends(_employee_salary_service),
) -> Response:
    await service.delete(salary_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ══════════════════════════════════════════════
# Employee Salary Components
# ══════════════════════════════════════════════
employee_salary_component_router = APIRouter(prefix="/employee-salary-components", dependencies=[_read_perm])


@employee_salary_component_router.post(
    "", response_model=EmployeeSalaryComponentRead, status_code=status.HTTP_201_CREATED, dependencies=[_process_perm]
)
async def create_employee_salary_component(
    payload: EmployeeSalaryComponentCreate,
    service: EmployeeSalaryComponentService = Depends(_employee_salary_component_service),
) -> EmployeeSalaryComponentRead:
    return await service.create(payload)


@employee_salary_component_router.get("", response_model=EmployeeSalaryComponentList)
async def list_employee_salary_components(
    employee_salary_id: int | None = None,
    salary_component_id: int | None = None,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    service: EmployeeSalaryComponentService = Depends(_employee_salary_component_service),
) -> EmployeeSalaryComponentList:
    return await service.list(
        employee_salary_id=employee_salary_id,
        salary_component_id=salary_component_id,
        offset=offset,
        limit=limit,
    )


@employee_salary_component_router.get("/{component_id}", response_model=EmployeeSalaryComponentRead)
async def get_employee_salary_component(
    component_id: int,
    service: EmployeeSalaryComponentService = Depends(_employee_salary_component_service),
) -> EmployeeSalaryComponentRead:
    return await service.get(component_id)


@employee_salary_component_router.patch("/{component_id}", response_model=EmployeeSalaryComponentRead, dependencies=[_process_perm])
async def update_employee_salary_component(
    component_id: int,
    payload: EmployeeSalaryComponentUpdate,
    service: EmployeeSalaryComponentService = Depends(_employee_salary_component_service),
) -> EmployeeSalaryComponentRead:
    return await service.update(component_id, payload)


@employee_salary_component_router.delete("/{component_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[_process_perm])
async def delete_employee_salary_component(
    component_id: int,
    service: EmployeeSalaryComponentService = Depends(_employee_salary_component_service),
) -> Response:
    await service.delete(component_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ══════════════════════════════════════════════
# Employee Payslips
# ══════════════════════════════════════════════
employee_payslip_router = APIRouter(prefix="/employee-payslips", dependencies=[_read_perm])


@employee_payslip_router.post("", response_model=EmployeePayslipRead, status_code=status.HTTP_201_CREATED, dependencies=[_process_perm])
async def create_employee_payslip(
    payload: EmployeePayslipCreate,
    service: EmployeePayslipService = Depends(_employee_payslip_service),
    employee_id: str | None = Depends(get_current_employee_id),
) -> EmployeePayslipRead:
    return await service.create(payload, employee_id=employee_id)


@employee_payslip_router.post("/generate", response_model=EmployeePayslipGenerateResult, dependencies=[_process_perm])
async def generate_employee_payslips(
    payload: EmployeePayslipGenerateRequest,
    service: EmployeePayslipService = Depends(_employee_payslip_service),
    employee_id: str | None = Depends(get_current_employee_id),
) -> EmployeePayslipGenerateResult:
    return await service.generate(
        month=payload.month,
        year=payload.year,
        generated_by=employee_id,
    )


@employee_payslip_router.get("", response_model=EmployeePayslipList)
async def list_employee_payslips(
    employee_id: str | None = None,
    employee_salary_id: int | None = None,
    year: int | None = None,
    month: int | None = None,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    service: EmployeePayslipService = Depends(_employee_payslip_service),
    can_view_draft: bool = Depends(_can_view_draft),
) -> EmployeePayslipList:
    return await service.list(
        employee_id=employee_id,
        employee_salary_id=employee_salary_id,
        year=year,
        month=month,
        offset=offset,
        limit=limit,
        can_view_draft=can_view_draft,
    )


@employee_payslip_router.get("/{payslip_id}", response_model=EmployeePayslipRead)
async def get_employee_payslip(
    payslip_id: int,
    service: EmployeePayslipService = Depends(_employee_payslip_service),
    can_view_draft: bool = Depends(_can_view_draft),
) -> EmployeePayslipRead:
    return await service.get(payslip_id, can_view_draft=can_view_draft)


@employee_payslip_router.patch("/{payslip_id}", response_model=EmployeePayslipRead, dependencies=[_process_perm])
async def update_employee_payslip(
    payslip_id: int,
    payload: EmployeePayslipUpdate,
    service: EmployeePayslipService = Depends(_employee_payslip_service),
) -> EmployeePayslipRead:
    return await service.update(payslip_id, payload)


@employee_payslip_router.delete("/{payslip_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[_process_perm])
async def delete_employee_payslip(
    payslip_id: int,
    service: EmployeePayslipService = Depends(_employee_payslip_service),
) -> Response:
    await service.delete(payslip_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Register all sub-routers
router.include_router(salary_component_router)
router.include_router(employee_salary_router)
router.include_router(employee_salary_component_router)
router.include_router(employee_payslip_router)
