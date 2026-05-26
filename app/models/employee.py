import re
import uuid
from datetime import datetime, date
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, DateTime, Text, Integer, Date, Index, Select, select, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates, object_session

from app.db.base import Base
from app.models.mixins import TenantMixin, AuditableMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.company import Company
    from app.models.department import Department
    from app.models.designation import Designation
    from app.models.grade import Grade
    from app.models.location import Location
    from app.models.business_unit import BusinessUnit
    from app.models.employee_personal_detail import EmployeePersonalDetail
    from app.models.employee_bank_detail import EmployeeBankDetail
    from app.models.employee_document import EmployeeDocument
    from app.models.employee_lifecycle_event import EmployeeLifecycleEvent
    from app.models.employee_custom_field_value import EmployeeCustomFieldValue
    from app.models.leave_balance import LeaveBalance
    from app.models.leave_request import LeaveRequest
    from app.models.shift_assignment import ShiftAssignment
    from app.models.attendance_record import AttendanceRecord
    from app.models.attendance_regularization import AttendanceRegularization
    from app.models.attendance_summary import AttendanceSummary
    from app.models.overtime_record import OvertimeRecord
    from app.models.comp_off_credit import CompOffCredit
    from app.models.wfh_request import WfhRequest


class Employee(TenantMixin, AuditableMixin, Base):
    __tablename__ = "employees"

    EMPLOYMENT_TYPES = ("full_time", "part_time", "contract", "intern")
    EMPLOYMENT_STATUSES = ("active", "on_notice", "relieved", "absconding", "terminated", "retired")
    GENDERS = ("male", "female", "other", "undisclosed")
    ONBOARDING_STATUSES = ("invited", "password_set", "profile_incomplete", "active")
    WORK_MODES = ("office", "wfh", "hybrid")

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    designation_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("designations.id"), nullable=True)
    grade_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("grades.id"), nullable=True)
    location_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("locations.id"), nullable=True)
    business_unit_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("business_units.id"), nullable=True)
    reporting_manager_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)

    employee_number: Mapped[str] = mapped_column(String(50), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    email_official: Mapped[str] = mapped_column(String(255), nullable=False)
    email_personal: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    date_of_birth: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    marital_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    blood_group: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    nationality: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    profile_photo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    date_of_joining: Mapped[datetime] = mapped_column(Date, nullable=False)
    date_of_confirmation: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    probation_end_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    date_of_exit: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    notice_period_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    employment_type: Mapped[str] = mapped_column(String(20), nullable=False)
    employment_status: Mapped[str] = mapped_column(String(20), nullable=False)
    exit_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    onboarding_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    work_mode: Mapped[str] = mapped_column(String(20), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    user: Mapped["User"] = relationship("User")
    company: Mapped["Company"] = relationship("Company")
    department: Mapped[Optional["Department"]] = relationship("Department")
    designation: Mapped[Optional["Designation"]] = relationship("Designation")
    grade: Mapped[Optional["Grade"]] = relationship("Grade")
    location: Mapped[Optional["Location"]] = relationship("Location")
    business_unit: Mapped[Optional["BusinessUnit"]] = relationship("BusinessUnit")
    reporting_manager: Mapped[Optional["Employee"]] = relationship("Employee", remote_side="Employee.id")
    direct_reports: Mapped[list["Employee"]] = relationship("Employee")

    personal_detail: Mapped[Optional["EmployeePersonalDetail"]] = relationship("EmployeePersonalDetail", uselist=False, cascade="all, delete-orphan")
    bank_details: Mapped[list["EmployeeBankDetail"]] = relationship("EmployeeBankDetail", cascade="all, delete-orphan")
    documents: Mapped[list["EmployeeDocument"]] = relationship("EmployeeDocument", cascade="all, delete-orphan")
    lifecycle_events: Mapped[list["EmployeeLifecycleEvent"]] = relationship("EmployeeLifecycleEvent", cascade="all, delete-orphan")
    custom_field_values: Mapped[list["EmployeeCustomFieldValue"]] = relationship("EmployeeCustomFieldValue", cascade="all, delete-orphan")
    leave_balances: Mapped[list["LeaveBalance"]] = relationship("LeaveBalance", cascade="all, delete-orphan")
    leave_requests: Mapped[list["LeaveRequest"]] = relationship("LeaveRequest", cascade="all, delete-orphan")
    shift_assignments: Mapped[list["ShiftAssignment"]] = relationship("ShiftAssignment", cascade="all, delete-orphan")
    attendance_records: Mapped[list["AttendanceRecord"]] = relationship("AttendanceRecord", cascade="all, delete-orphan")
    attendance_regularizations: Mapped[list["AttendanceRegularization"]] = relationship("AttendanceRegularization", cascade="all, delete-orphan")
    attendance_summaries: Mapped[list["AttendanceSummary"]] = relationship("AttendanceSummary", cascade="all, delete-orphan")
    overtime_records: Mapped[list["OvertimeRecord"]] = relationship("OvertimeRecord", cascade="all, delete-orphan")
    comp_off_credits: Mapped[list["CompOffCredit"]] = relationship("CompOffCredit", cascade="all, delete-orphan")
    wfh_requests: Mapped[list["WfhRequest"]] = relationship("WfhRequest", cascade="all, delete-orphan")

    __table_args__ = (
        Index("index_employees_on_tenant_id_and_employee_number", "tenant_id", "employee_number", unique=True),
        Index("index_employees_on_tenant_id_and_user_id", "tenant_id", "user_id", unique=True),
        Index("index_employees_on_business_unit_id", "business_unit_id"),
        Index("index_employees_on_company_id", "company_id"),
        Index("index_employees_on_date_of_joining", "date_of_joining"),
        Index("index_employees_on_department_id", "department_id"),
        Index("index_employees_on_designation_id", "designation_id"),
        Index("index_employees_on_employment_status", "employment_status"),
        Index("index_employees_on_grade_id", "grade_id"),
        Index("index_employees_on_location_id", "location_id"),
        Index("index_employees_on_onboarding_status", "onboarding_status"),
        Index("index_employees_on_reporting_manager_id", "reporting_manager_id"),
        Index("index_employees_on_tenant_id", "tenant_id"),
        Index("index_employees_on_user_id", "user_id"),
        Index("index_employees_on_work_mode", "work_mode"),
    )

    @classmethod
    def active(cls) -> Select:
        return select(cls).where(cls.employment_status == "active")

    @classmethod
    def in_department(cls, dept_id: uuid.UUID) -> Select:
        return select(cls).where(cls.department_id == dept_id)

    @classmethod
    def reporting_to(cls, manager_id: uuid.UUID) -> Select:
        return select(cls).where(cls.reporting_manager_id == manager_id)

    @property
    def full_name(self) -> str:
        parts = [p for p in [self.first_name, self.middle_name, self.last_name] if p and p.strip()]
        return " ".join(parts)

    def active_employee(self) -> bool:
        return self.employment_status == "active"

    def onboarding_complete(self) -> bool:
        return self.onboarding_status == "active"

    def permanent_wfh(self) -> bool:
        return self.work_mode == "wfh"

    def wfh_eligible(self) -> bool:
        return self.work_mode in ("wfh", "hybrid")

    def current_shift(self):
        from app.models.shift_assignment import ShiftAssignment
        today = date.today()
        stmt = (
            select(ShiftAssignment)
            .where(
                ShiftAssignment.employee_id == self.id,
                ShiftAssignment.effective_from <= today,
                (ShiftAssignment.effective_to.is_(None)) | (ShiftAssignment.effective_to >= today),
            )
            .order_by(ShiftAssignment.effective_from.desc())
            .limit(1)
        )
        session = object_session(self)
        assignment = session.execute(stmt).scalar_one_or_none()
        return assignment.shift if assignment else None

    @validates("employee_number")
    def validate_employee_number(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Employee number cannot be empty")
        return value

    @validates("first_name")
    def validate_first_name(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("First name cannot be empty")
        if len(value) > 100:
            raise ValueError("First name is too long (maximum is 100 characters)")
        return value

    @validates("last_name")
    def validate_last_name(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Last name cannot be empty")
        if len(value) > 100:
            raise ValueError("Last name is too long (maximum is 100 characters)")
        return value

    @validates("email_official")
    def validate_email_official(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Official email cannot be empty")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError("Official email is not a valid email")
        return value

    @validates("date_of_joining")
    def validate_date_of_joining(self, key: str, value: datetime) -> datetime:
        if value is None:
            raise ValueError("Date of joining cannot be empty")
        return value

    @validates("employment_type")
    def validate_employment_type(self, key: str, value: str) -> str:
        if value not in self.EMPLOYMENT_TYPES:
            raise ValueError(f"Employment type must be one of {self.EMPLOYMENT_TYPES}")
        return value

    @validates("employment_status")
    def validate_employment_status(self, key: str, value: str) -> str:
        if value not in self.EMPLOYMENT_STATUSES:
            raise ValueError(f"Employment status must be one of {self.EMPLOYMENT_STATUSES}")
        return value

    @validates("gender")
    def validate_gender(self, key: str, value: Optional[str]) -> Optional[str]:
        if value is not None and value not in self.GENDERS:
            raise ValueError(f"Gender must be one of {self.GENDERS}")
        return value

    @validates("onboarding_status")
    def validate_onboarding_status(self, key: str, value: Optional[str]) -> Optional[str]:
        if value is not None and value not in self.ONBOARDING_STATUSES:
            raise ValueError(f"Onboarding status must be one of {self.ONBOARDING_STATUSES}")
        return value

    @validates("work_mode")
    def validate_work_mode(self, key: str, value: Optional[str]) -> Optional[str]:
        if value is not None and value not in self.WORK_MODES:
            raise ValueError(f"Work mode must be one of {self.WORK_MODES}")
        return value

    @validates("reporting_manager_id")
    def validate_reporting_manager_id(self, key: str, value: Optional[uuid.UUID]) -> Optional[uuid.UUID]:
        if value is not None:
            if value == self.id:
                raise ValueError("Reporting manager cannot be yourself")
            visited = {self.id}
            current = value
            while current is not None:
                if current in visited:
                    raise ValueError("Reporting manager creates a circular reporting chain")
                visited.add(current)
                session = object_session(self)
                result = session.execute(
                    select(Employee.reporting_manager_id).where(Employee.id == current)
                ).scalar_one_or_none()
                current = result
        return value
