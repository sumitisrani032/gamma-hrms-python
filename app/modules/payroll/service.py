from datetime import date
from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.modules.payroll.constants import (
    EMPLOYEE_PAYSLIP_NOT_FOUND,
    EMPLOYEE_SALARY_COMPONENT_NOT_FOUND,
    EMPLOYEE_SALARY_NOT_FOUND,
    SALARY_COMPONENT_NOT_FOUND,
)
from app.modules.payroll.model import EmployeePayslip, EmployeeSalary, SalaryComponent
from app.modules.payroll.repository import (
    EmployeePayslipRepository,
    EmployeeSalaryComponentRepository,
    EmployeeSalaryRepository,
    SalaryComponentRepository,
)
from app.modules.payroll.schema import (
    EmployeePayslipCreate,
    EmployeePayslipGenerateRequest,
    EmployeePayslipGenerateResult,
    EmployeePayslipGenerateResultItem,
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


# ──────────────────────────────────────────────
# SalaryComponentService
# ──────────────────────────────────────────────
class SalaryComponentService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = SalaryComponentRepository(db)

    async def create(self, payload: SalaryComponentCreate, employee_id: str | None = None) -> SalaryComponentRead:
        if employee_id and payload.created_by is None:
            payload.created_by = UUID(employee_id)
        obj = await self.repository.create(payload)
        return SalaryComponentRead.model_validate(obj)

    async def list(
        self,
        *,
        is_active: bool | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> SalaryComponentList:
        items, total = await self.repository.list(is_active=is_active, offset=offset, limit=limit)
        return SalaryComponentList(
            items=[SalaryComponentRead.model_validate(o) for o in items],
            total=total,
        )

    async def get(self, obj_id: int) -> SalaryComponentRead:
        obj = await self.repository.get(obj_id)
        if obj is None:
            raise NotFoundException(SALARY_COMPONENT_NOT_FOUND)
        return SalaryComponentRead.model_validate(obj)

    async def update(self, obj_id: int, payload: SalaryComponentUpdate) -> SalaryComponentRead:
        obj = await self.repository.get(obj_id)
        if obj is None:
            raise NotFoundException(SALARY_COMPONENT_NOT_FOUND)
        updated = await self.repository.update(obj, payload)
        return SalaryComponentRead.model_validate(updated)

    async def delete(self, obj_id: int) -> None:
        obj = await self.repository.get(obj_id)
        if obj is None:
            raise NotFoundException(SALARY_COMPONENT_NOT_FOUND)
        await self.repository.delete(obj)


# ──────────────────────────────────────────────
# EmployeeSalaryService
# ──────────────────────────────────────────────
class EmployeeSalaryService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = EmployeeSalaryRepository(db)

    async def create(self, payload: EmployeeSalaryCreate, employee_id: str | None = None) -> EmployeeSalaryRead:
        if employee_id and payload.created_by is None:
            payload.created_by = UUID(employee_id)
        obj = await self.repository.create(payload)
        return EmployeeSalaryRead.model_validate(obj)

    async def _fetch_employee_names(self, employee_ids: list[UUID]) -> dict[UUID, str]:
        if not employee_ids:
            return {}
        result = await self.db.execute(
            text("""
                SELECT id, CONCAT_WS(' ', first_name, middle_name, last_name) AS name
                FROM employees WHERE id = ANY(:ids)
            """),
            {"ids": list(employee_ids)},
        )
        return {row[0]: row[1] for row in result}

    async def list(
        self,
        *,
        employee_id: str | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> EmployeeSalaryList:
        items, total = await self.repository.list(employee_id=employee_id, offset=offset, limit=limit)
        dtos = [EmployeeSalaryRead.model_validate(o) for o in items]
        if dtos:
            name_map = await self._fetch_employee_names([d.employee_id for d in dtos])
            for d in dtos:
                d.employee_name = name_map.get(d.employee_id)
        return EmployeeSalaryList(items=dtos, total=total)

    async def get(self, obj_id: int) -> EmployeeSalaryRead:
        obj = await self.repository.get(obj_id)
        if obj is None:
            raise NotFoundException(EMPLOYEE_SALARY_NOT_FOUND)
        return EmployeeSalaryRead.model_validate(obj)

    async def update(self, obj_id: int, payload: EmployeeSalaryUpdate) -> EmployeeSalaryRead:
        obj = await self.repository.get(obj_id)
        if obj is None:
            raise NotFoundException(EMPLOYEE_SALARY_NOT_FOUND)
        updated = await self.repository.update(obj, payload)
        return EmployeeSalaryRead.model_validate(updated)

    async def delete(self, obj_id: int) -> None:
        obj = await self.repository.get(obj_id)
        if obj is None:
            raise NotFoundException(EMPLOYEE_SALARY_NOT_FOUND)
        await self.repository.delete(obj)


# ──────────────────────────────────────────────
# EmployeeSalaryComponentService
# ──────────────────────────────────────────────
class EmployeeSalaryComponentService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = EmployeeSalaryComponentRepository(db)

    async def create(self, payload: EmployeeSalaryComponentCreate) -> EmployeeSalaryComponentRead:
        obj = await self.repository.create(payload)
        return EmployeeSalaryComponentRead.model_validate(obj)

    async def list(
        self,
        *,
        employee_salary_id: int | None = None,
        salary_component_id: int | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> EmployeeSalaryComponentList:
        items, total = await self.repository.list(
            employee_salary_id=employee_salary_id,
            salary_component_id=salary_component_id,
            offset=offset,
            limit=limit,
        )
        return EmployeeSalaryComponentList(
            items=[EmployeeSalaryComponentRead.model_validate(o) for o in items],
            total=total,
        )

    async def get(self, obj_id: int) -> EmployeeSalaryComponentRead:
        obj = await self.repository.get(obj_id)
        if obj is None:
            raise NotFoundException(EMPLOYEE_SALARY_COMPONENT_NOT_FOUND)
        return EmployeeSalaryComponentRead.model_validate(obj)

    async def update(
        self, obj_id: int, payload: EmployeeSalaryComponentUpdate
    ) -> EmployeeSalaryComponentRead:
        obj = await self.repository.get(obj_id)
        if obj is None:
            raise NotFoundException(EMPLOYEE_SALARY_COMPONENT_NOT_FOUND)
        updated = await self.repository.update(obj, payload)
        return EmployeeSalaryComponentRead.model_validate(updated)

    async def delete(self, obj_id: int) -> None:
        obj = await self.repository.get(obj_id)
        if obj is None:
            raise NotFoundException(EMPLOYEE_SALARY_COMPONENT_NOT_FOUND)
        await self.repository.delete(obj)


# ──────────────────────────────────────────────
# EmployeePayslipService
# ──────────────────────────────────────────────
class EmployeePayslipService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = EmployeePayslipRepository(db)

    async def create(self, payload: EmployeePayslipCreate, employee_id: str | None = None) -> EmployeePayslipRead:
        if employee_id and payload.generated_by is None:
            payload.generated_by = UUID(employee_id)
        obj = await self.repository.create(payload)
        return EmployeePayslipRead.model_validate(obj)

    async def _fetch_employee_names(self, employee_ids: list[UUID]) -> dict[UUID, str]:
        if not employee_ids:
            return {}
        result = await self.db.execute(
            text("""
                SELECT id, CONCAT_WS(' ', first_name, middle_name, last_name) AS name
                FROM employees WHERE id = ANY(:ids)
            """),
            {"ids": list(employee_ids)},
        )
        return {row[0]: row[1] for row in result}

    async def _fetch_employee_details(self, employee_ids: list[UUID]) -> dict[UUID, dict]:
        if not employee_ids:
            return {}
        result = await self.db.execute(
            text("""
                SELECT
                    e.id,
                    e.company_id,
                    CONCAT_WS(' ', e.first_name, e.middle_name, e.last_name) AS name,
                    d.name AS designation,
                    dept.name AS department,
                    e.date_of_joining::text,
                    l.name AS location_name
                FROM employees e
                LEFT JOIN designations d ON d.id = e.designation_id
                LEFT JOIN departments dept ON dept.id = e.department_id
                LEFT JOIN locations l ON l.id = e.location_id
                WHERE e.id = ANY(:ids)
            """),
            {"ids": list(employee_ids)},
        )
        return {
            row[0]: {
                "name": row[2],
                "company_id": row[1],
                "designation": row[3],
                "department": row[4],
                "date_of_joining": row[5],
                "work_location": row[6],
            }
            for row in result
        }

    async def _fetch_company_info(self, company_ids: list[UUID]) -> dict[UUID, dict]:
        if not company_ids:
            return {}
        result = await self.db.execute(
            text("""
                SELECT id, name, legal_name, address, tax_id, registration_number
                FROM companies WHERE id = ANY(:ids)
            """),
            {"ids": list(company_ids)},
        )
        return {
            row[0]: {
                "name": row[1] or row[2],
                "address": row[3],
                "tax_id": row[4],
                "registration_number": row[5],
            }
            for row in result
        }

    async def _enrich_payslip_dtos(self, dtos: list[EmployeePayslipRead]) -> None:
        if not dtos:
            return
        employee_ids = list({d.employee_id for d in dtos})
        emp_map = await self._fetch_employee_details(employee_ids)
        company_ids = [v["company_id"] for v in emp_map.values() if v.get("company_id")]
        comp_map = await self._fetch_company_info(company_ids) if company_ids else {}
        for d in dtos:
            emp = emp_map.get(d.employee_id)
            if emp:
                d.employee_name = emp["name"]
                d.employee_designation = emp["designation"]
                d.employee_department = emp["department"]
                d.date_of_joining = emp["date_of_joining"]
                d.work_location = emp["work_location"]
                comp = comp_map.get(emp["company_id"])
                if comp:
                    d.company_name = comp["name"]
                    d.company_address = comp["address"]
                    d.company_tax_id = comp["tax_id"]
                    d.company_registration_number = comp["registration_number"]

    async def generate(
        self,
        month: int,
        year: int,
        generated_by: str | None = None,
    ) -> EmployeePayslipGenerateResult:
        # Fetch all non-draft salaries
        salary_stmt = select(EmployeeSalary).where(EmployeeSalary.status != "draft")
        salary_result = await self.db.scalars(salary_stmt)
        all_salaries = list(salary_result.all())

        # Fetch all active salary components master
        comp_stmt = select(SalaryComponent).where(SalaryComponent.is_active == True)
        comp_result = await self.db.scalars(comp_stmt)
        master_components = {c.id: c for c in comp_result.all()}

        # Fetch employee names for result display
        emp_ids = [s.employee_id for s in all_salaries]
        emp_map = await self._fetch_employee_names(emp_ids)

        items: list[EmployeePayslipGenerateResultItem] = []
        created_count = 0
        skipped_count = 0
        failed_count = 0
        gen_by = UUID(generated_by) if generated_by else None
        today = date.today()

        for salary in all_salaries:

            try:
                # Fetch the current editable component setup for this salary.
                from app.modules.payroll.model import EmployeeSalaryComponent
                link_result = await self.db.execute(
                    select(EmployeeSalaryComponent).where(
                        EmployeeSalaryComponent.employee_salary_id == salary.id
                    )
                )
                links = list(link_result.scalars().all())

                earnings: dict[str, float] = {}
                deductions: dict[str, float] = {}
                gross = 0.0
                deduction_total = 0.0

                for link in links:
                    master = master_components.get(link.salary_component_id)
                    if not master:
                        continue
                    amount = float(link.monthly_amount) if link.monthly_amount else 0.0
                    key = master.code
                    if master.type == "earning":
                        earnings[key] = amount
                        gross += amount
                    else:
                        deductions[key] = amount
                        deduction_total += amount

                net = gross - deduction_total

                payslip = EmployeePayslip(
                    employee_id=salary.employee_id,
                    employee_salary_id=salary.id,
                    month=month,
                    year=year,
                    component_snapshot={"earnings": earnings, "deductions": deductions},
                    gross_amount=gross,
                    deduction_amount=deduction_total,
                    net_amount=net,
                    generated_on=today,
                    generated_by=gen_by or salary.created_by,
                    status="draft",
                    total_attendance=30,
                    paid_days=30,
                )
                self.db.add(payslip)
                await self.db.flush()

                items.append(EmployeePayslipGenerateResultItem(
                    employee_id=salary.employee_id,
                    employee_name=emp_map.get(salary.employee_id),
                    status="created",
                ))
                created_count += 1
            except Exception:
                items.append(EmployeePayslipGenerateResultItem(
                    employee_id=salary.employee_id,
                    employee_name=emp_map.get(salary.employee_id),
                    status="failed",
                    message="Failed to generate",
                ))
                failed_count += 1

        await self.db.commit()

        return EmployeePayslipGenerateResult(
            items=items,
            total_requested=len(all_salaries),
            total_created=created_count,
            total_skipped=skipped_count,
            total_failed=failed_count,
        )

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
    ) -> EmployeePayslipList:
        items, total = await self.repository.list(
            employee_id=employee_id,
            employee_salary_id=employee_salary_id,
            year=year,
            month=month,
            offset=offset,
            limit=limit,
            can_view_draft=can_view_draft,
        )
        dtos = [EmployeePayslipRead.model_validate(o) for o in items]
        await self._enrich_payslip_dtos(dtos)
        return EmployeePayslipList(items=dtos, total=total)

    async def get(self, obj_id: int, can_view_draft: bool = True) -> EmployeePayslipRead:
        obj = await self.repository.get(obj_id)
        if obj is None:
            raise NotFoundException(EMPLOYEE_PAYSLIP_NOT_FOUND)
        if not can_view_draft and obj.status == "draft":
            raise NotFoundException(EMPLOYEE_PAYSLIP_NOT_FOUND)
        dto = EmployeePayslipRead.model_validate(obj)
        await self._enrich_payslip_dtos([dto])
        return dto

    async def update(self, obj_id: int, payload: EmployeePayslipUpdate) -> EmployeePayslipRead:
        obj = await self.repository.get(obj_id)
        if obj is None:
            raise NotFoundException(EMPLOYEE_PAYSLIP_NOT_FOUND)
        updated = await self.repository.update(obj, payload)
        return EmployeePayslipRead.model_validate(updated)

    async def delete(self, obj_id: int) -> None:
        obj = await self.repository.get(obj_id)
        if obj is None:
            raise NotFoundException(EMPLOYEE_PAYSLIP_NOT_FOUND)
        await self.repository.delete(obj)
