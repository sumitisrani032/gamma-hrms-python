from app.db.base import Base

from app.models.tenant import Tenant
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user_role import UserRole
from app.models.attachment import Attachment
from app.models.audit_log import AuditLog
from app.models.notification import Notification

from app.models.company import Company
from app.models.location import Location
from app.models.grade import Grade
from app.models.designation import Designation
from app.models.business_unit import BusinessUnit
from app.models.department import Department
from app.models.employee import Employee
from app.models.employee_personal_detail import EmployeePersonalDetail
from app.models.employee_bank_detail import EmployeeBankDetail
from app.models.employee_document import EmployeeDocument
from app.models.employee_lifecycle_event import EmployeeLifecycleEvent
from app.models.employee_custom_field_definition import EmployeeCustomFieldDefinition
from app.models.employee_custom_field_value import EmployeeCustomFieldValue
from app.models.document_requirement import DocumentRequirement

from app.models.leave_type import LeaveType
from app.models.leave_policy import LeavePolicy
from app.models.leave_balance import LeaveBalance
from app.models.leave_request import LeaveRequest

from app.models.holiday_calendar import HolidayCalendar
from app.models.holiday import Holiday
from app.models.shift import Shift
from app.models.shift_assignment import ShiftAssignment
from app.models.attendance_record import AttendanceRecord
from app.models.attendance_regularization import AttendanceRegularization
from app.models.attendance_summary import AttendanceSummary
from app.models.attendance_session import AttendanceSession

from app.models.overtime_rule import OvertimeRule
from app.models.overtime_record import OvertimeRecord
from app.models.comp_off_credit import CompOffCredit

from app.models.wfh_policy import WfhPolicy
from app.models.wfh_request import WfhRequest

from app.models.workflow_definition import WorkflowDefinition
from app.models.workflow_step import WorkflowStep
from app.models.workflow_instance import WorkflowInstance
from app.models.workflow_step_instance import WorkflowStepInstance

from app.models.policy_document import PolicyDocument
from app.models.policy_acknowledgement import PolicyAcknowledgement

# Context storage (not a DB model — mirrors Rails' CurrentAttributes)
from app.models.current import Current

__all__ = [
    "Base",
    "Tenant",
    "User",
    "RefreshToken",
    "Permission",
    "Role",
    "RolePermission",
    "UserRole",
    "Attachment",
    "AuditLog",
    "Notification",
    "Company",
    "Location",
    "Grade",
    "Designation",
    "BusinessUnit",
    "Department",
    "Employee",
    "EmployeePersonalDetail",
    "EmployeeBankDetail",
    "EmployeeDocument",
    "EmployeeLifecycleEvent",
    "EmployeeCustomFieldDefinition",
    "EmployeeCustomFieldValue",
    "DocumentRequirement",
    "LeaveType",
    "LeavePolicy",
    "LeaveBalance",
    "LeaveRequest",
    "HolidayCalendar",
    "Holiday",
    "Shift",
    "ShiftAssignment",
    "AttendanceRecord",
    "AttendanceRegularization",
    "AttendanceSummary",
    "AttendanceSession",
    "OvertimeRule",
    "OvertimeRecord",
    "CompOffCredit",
    "WfhPolicy",
    "WfhRequest",
    "WorkflowDefinition",
    "WorkflowStep",
    "WorkflowInstance",
    "WorkflowStepInstance",
    "PolicyDocument",
    "PolicyAcknowledgement",
    "Current",
]
