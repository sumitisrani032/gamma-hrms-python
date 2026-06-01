from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.payroll.model import (
    EmployeePayslip,
    EmployeeSalary,
    EmployeeSalaryComponent,
    SalaryComponent,
)
from app.modules.payroll.schema import (
    EmployeePayslipCreate,
    EmployeePayslipUpdate,
    EmployeeSalaryComponentCreate,
    EmployeeSalaryComponentUpdate,
    EmployeeSalaryCreate,
    EmployeeSalaryUpdate,
    SalaryComponentCreate,
    SalaryComponentUpdate,
)


# ──────────────────────────────────────────────
# SalaryComponentRepository
# ──────────────────────────────────────────────
class SalaryComponentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, payload: SalaryComponentCreate) -> SalaryComponent:
        obj = SalaryComponent(**payload.model_dump(mode="python"))
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def list(
        self,
        *,
        is_active: bool | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> tuple[Sequence[SalaryComponent], int]:
        filters = []
        if is_active is not None:
            filters.append(SalaryComponent.is_active == is_active)

        total_stmt = select(func.count()).select_from(SalaryComponent).where(*filters)
        total = await self.db.scalar(total_stmt)

        stmt = (
            select(SalaryComponent)
            .where(*filters)
            .order_by(SalaryComponent.updated_at.desc(), SalaryComponent.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.scalars(stmt)
        return result.all(), total or 0

    async def get(self, obj_id: int) -> SalaryComponent | None:
        stmt = select(SalaryComponent).where(SalaryComponent.id == obj_id)
        return await self.db.scalar(stmt)

    async def update(self, obj: SalaryComponent, payload: SalaryComponentUpdate) -> SalaryComponent:
        for field, value in payload.model_dump(exclude_unset=True, mode="python").items():
            setattr(obj, field, value)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj: SalaryComponent) -> None:
        await self.db.delete(obj)
        await self.db.commit()


# ──────────────────────────────────────────────
# EmployeeSalaryRepository
# ──────────────────────────────────────────────
class EmployeeSalaryRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, payload: EmployeeSalaryCreate) -> EmployeeSalary:
        obj = EmployeeSalary(**payload.model_dump(mode="python"))
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def list(
        self,
        *,
        employee_id: str | None = None,
        employee_ids: list[str] | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> tuple[Sequence[EmployeeSalary], int]:
        filters = []
        if employee_id is not None:
            filters.append(EmployeeSalary.employee_id == employee_id)
        if employee_ids is not None:
            filters.append(EmployeeSalary.employee_id.in_(employee_ids))

        total_stmt = select(func.count()).select_from(EmployeeSalary).where(*filters)
        total = await self.db.scalar(total_stmt)

        stmt = (
            select(EmployeeSalary)
            .where(*filters)
            .order_by(EmployeeSalary.updated_at.desc(), EmployeeSalary.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.scalars(stmt)
        return result.all(), total or 0

    async def get(self, obj_id: int) -> EmployeeSalary | None:
        stmt = select(EmployeeSalary).where(EmployeeSalary.id == obj_id)
        return await self.db.scalar(stmt)

    async def update(self, obj: EmployeeSalary, payload: EmployeeSalaryUpdate) -> EmployeeSalary:
        for field, value in payload.model_dump(exclude_unset=True, mode="python").items():
            setattr(obj, field, value)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj: EmployeeSalary) -> None:
        await self.db.delete(obj)
        await self.db.commit()


# ──────────────────────────────────────────────
# EmployeeSalaryComponentRepository
# ──────────────────────────────────────────────
class EmployeeSalaryComponentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, payload: EmployeeSalaryComponentCreate) -> EmployeeSalaryComponent:
        obj = EmployeeSalaryComponent(**payload.model_dump(mode="python"))
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def list(
        self,
        *,
        employee_salary_id: int | None = None,
        salary_component_id: int | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> tuple[Sequence[EmployeeSalaryComponent], int]:
        filters = []
        if employee_salary_id is not None:
            filters.append(EmployeeSalaryComponent.employee_salary_id == employee_salary_id)
        if salary_component_id is not None:
            filters.append(EmployeeSalaryComponent.salary_component_id == salary_component_id)

        total_stmt = select(func.count()).select_from(EmployeeSalaryComponent).where(*filters)
        total = await self.db.scalar(total_stmt)

        stmt = (
            select(EmployeeSalaryComponent)
            .where(*filters)
            .order_by(EmployeeSalaryComponent.updated_at.desc(), EmployeeSalaryComponent.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.scalars(stmt)
        return result.all(), total or 0

    async def get(self, obj_id: int) -> EmployeeSalaryComponent | None:
        stmt = select(EmployeeSalaryComponent).where(EmployeeSalaryComponent.id == obj_id)
        return await self.db.scalar(stmt)

    async def update(
        self, obj: EmployeeSalaryComponent, payload: EmployeeSalaryComponentUpdate
    ) -> EmployeeSalaryComponent:
        for field, value in payload.model_dump(exclude_unset=True, mode="python").items():
            setattr(obj, field, value)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj: EmployeeSalaryComponent) -> None:
        await self.db.delete(obj)
        await self.db.commit()


# ──────────────────────────────────────────────
# EmployeePayslipRepository
# ──────────────────────────────────────────────
class EmployeePayslipRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, payload: EmployeePayslipCreate) -> EmployeePayslip:
        obj = EmployeePayslip(**payload.model_dump(mode="python"))
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def list(
        self,
        *,
        employee_id: str | None = None,
        employee_salary_id: int | None = None,
        year: int | None = None,
        month: int | None = None,
        offset: int = 0,
        limit: int = 100,
        can_view_draft: bool = True,
    ) -> tuple[Sequence[EmployeePayslip], int]:
        filters = []
        if employee_id is not None:
            filters.append(EmployeePayslip.employee_id == employee_id)
        if employee_salary_id is not None:
            filters.append(EmployeePayslip.employee_salary_id == employee_salary_id)
        if year is not None:
            filters.append(EmployeePayslip.year == year)
        if month is not None:
            filters.append(EmployeePayslip.month == month)
        if not can_view_draft:
            filters.append(EmployeePayslip.status.in_(["approved", "paid"]))

        total_stmt = select(func.count()).select_from(EmployeePayslip).where(*filters)
        total = await self.db.scalar(total_stmt)

        stmt = (
            select(EmployeePayslip)
            .where(*filters)
            .order_by(EmployeePayslip.year.desc(), EmployeePayslip.month.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.scalars(stmt)
        return result.all(), total or 0

    async def get(self, obj_id: int) -> EmployeePayslip | None:
        stmt = select(EmployeePayslip).where(EmployeePayslip.id == obj_id)
        return await self.db.scalar(stmt)

    async def update(self, obj: EmployeePayslip, payload: EmployeePayslipUpdate) -> EmployeePayslip:
        for field, value in payload.model_dump(exclude_unset=True, mode="python").items():
            setattr(obj, field, value)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj: EmployeePayslip) -> None:
        await self.db.delete(obj)
        await self.db.commit()
