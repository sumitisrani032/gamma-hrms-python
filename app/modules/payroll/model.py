from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import Date, ForeignKey, Integer, Numeric, Text, func, text
from sqlalchemy.dialects.postgresql import BIGINT, BOOLEAN, JSONB, TIMESTAMP, UUID, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SalaryComponent(Base):
    __tablename__ = "salary_components"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    tenant_location_id: Mapped[UUID] = mapped_column(UUID, nullable=False)
    code: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[UUID] = mapped_column(UUID, nullable=False)
    is_active: Mapped[bool] = mapped_column(BOOLEAN, nullable=False)
    type: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    calculation_type: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    percentage_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    percentage_of: Mapped[Optional[str]] = mapped_column(VARCHAR(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()"), onupdate=func.now()
    )

    employee_salary_components: Mapped[list[EmployeeSalaryComponent]] = relationship(
        back_populates="salary_component",
    )


class EmployeeSalary(Base):
    __tablename__ = "employee_salaries"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    employee_id: Mapped[UUID] = mapped_column(UUID, nullable=False)
    annual_ctc: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[UUID] = mapped_column(UUID, nullable=False)
    approved_by: Mapped[Optional[UUID]] = mapped_column(UUID, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()"), onupdate=func.now()
    )

    components: Mapped[list[EmployeeSalaryComponent]] = relationship(back_populates="salary")
    payslips: Mapped[list[EmployeePayslip]] = relationship(back_populates="salary")


class EmployeeSalaryComponent(Base):
    __tablename__ = "employee_salary_components"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    employee_salary_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("employee_salaries.id"), nullable=False
    )
    salary_component_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("salary_components.id"), nullable=False
    )
    monthly_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()"), onupdate=func.now()
    )

    salary: Mapped[EmployeeSalary] = relationship(back_populates="components")
    salary_component: Mapped[SalaryComponent] = relationship(back_populates="employee_salary_components")


class EmployeePayslip(Base):
    __tablename__ = "employee_payslips"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    employee_id: Mapped[UUID] = mapped_column(UUID, nullable=False)
    employee_salary_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("employee_salaries.id"), nullable=False
    )
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    component_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    gross_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    net_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    deduction_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    generated_on: Mapped[date] = mapped_column(Date, nullable=False)
    generated_by: Mapped[UUID] = mapped_column(UUID, nullable=False)
    status: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()"), onupdate=func.now()
    )
    total_attendance: Mapped[int] = mapped_column(Integer, nullable=False)
    paid_days: Mapped[int] = mapped_column(Integer, nullable=False)
    lop_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)

    salary: Mapped[EmployeeSalary] = relationship(back_populates="payslips")
