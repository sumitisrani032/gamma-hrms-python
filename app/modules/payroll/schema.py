from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ──────────────────────────────────────────────
# SalaryComponent
# ──────────────────────────────────────────────
class SalaryComponentBase(BaseModel):
    tenant_location_id: UUID
    code: str
    name: str
    description: str | None = None
    created_by: UUID | None = None
    is_active: bool
    type: str
    calculation_type: str
    percentage_value: Decimal | None = None
    percentage_of: str | None = None


class SalaryComponentCreate(SalaryComponentBase):
    pass


class SalaryComponentUpdate(BaseModel):
    tenant_location_id: UUID | None = None
    code: str | None = None
    name: str | None = None
    description: str | None = None
    created_by: UUID | None = None
    is_active: bool | None = None
    type: str | None = None
    calculation_type: str | None = None
    percentage_value: Decimal | None = None
    percentage_of: str | None = None


class SalaryComponentRead(SalaryComponentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class SalaryComponentList(BaseModel):
    items: list[SalaryComponentRead]
    total: int


# ──────────────────────────────────────────────
# EmployeeSalary
# ──────────────────────────────────────────────
class EmployeeSalaryBase(BaseModel):
    employee_id: UUID
    annual_ctc: Decimal
    currency: str
    year: int
    status: str
    effective_from: date
    effective_to: date | None = None
    remarks: str | None = None
    created_by: UUID | None = None
    approved_by: UUID | None = None


class EmployeeSalaryCreate(EmployeeSalaryBase):
    pass


class EmployeeSalaryUpdate(BaseModel):
    employee_id: UUID | None = None
    annual_ctc: Decimal | None = None
    currency: str | None = None
    year: int | None = None
    status: str | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    remarks: str | None = None
    created_by: UUID | None = None
    approved_by: UUID | None = None


class EmployeeSalaryRead(EmployeeSalaryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_name: str | None = None
    created_at: datetime
    updated_at: datetime


class EmployeeSalaryList(BaseModel):
    items: list[EmployeeSalaryRead]
    total: int


# ──────────────────────────────────────────────
# EmployeeSalaryComponent
# ──────────────────────────────────────────────
class EmployeeSalaryComponentBase(BaseModel):
    employee_salary_id: int
    salary_component_id: int
    monthly_amount: Decimal


class EmployeeSalaryComponentCreate(EmployeeSalaryComponentBase):
    pass


class EmployeeSalaryComponentUpdate(BaseModel):
    employee_salary_id: int | None = None
    salary_component_id: int | None = None
    monthly_amount: Decimal | None = None


class EmployeeSalaryComponentRead(EmployeeSalaryComponentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class EmployeeSalaryComponentList(BaseModel):
    items: list[EmployeeSalaryComponentRead]
    total: int


# ──────────────────────────────────────────────
# EmployeePayslip
# ──────────────────────────────────────────────
class EmployeePayslipBase(BaseModel):
    employee_id: UUID
    employee_salary_id: int
    month: int
    year: int
    component_snapshot: dict
    gross_amount: Decimal
    net_amount: Decimal
    deduction_amount: Decimal
    generated_on: date
    generated_by: UUID | None = None
    status: str
    total_attendance: int
    paid_days: int
    lop_days: int | None = None


class EmployeePayslipCreate(EmployeePayslipBase):
    pass


class EmployeePayslipUpdate(BaseModel):
    employee_id: UUID | None = None
    employee_salary_id: int | None = None
    month: int | None = None
    year: int | None = None
    component_snapshot: dict | None = None
    gross_amount: Decimal | None = None
    net_amount: Decimal | None = None
    deduction_amount: Decimal | None = None
    generated_on: date | None = None
    generated_by: UUID | None = None
    status: str | None = None
    total_attendance: int | None = None
    paid_days: int | None = None
    lop_days: int | None = None


class EmployeePayslipRead(EmployeePayslipBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_name: str | None = None
    employee_designation: str | None = None
    employee_department: str | None = None
    date_of_joining: str | None = None
    work_location: str | None = None
    company_name: str | None = None
    company_address: str | None = None
    company_tax_id: str | None = None
    company_registration_number: str | None = None
    created_at: datetime
    updated_at: datetime


class EmployeePayslipList(BaseModel):
    items: list[EmployeePayslipRead]
    total: int


# ──────────────────────────────────────────────
# Payslip Generation
# ──────────────────────────────────────────────
class EmployeePayslipGenerateRequest(BaseModel):
    month: int
    year: int


class EmployeePayslipGenerateResultItem(BaseModel):
    employee_id: UUID
    employee_name: str | None = None
    status: str
    message: str | None = None


class EmployeePayslipGenerateResult(BaseModel):
    items: list[EmployeePayslipGenerateResultItem]
    total_requested: int
    total_created: int
    total_skipped: int
    total_failed: int
