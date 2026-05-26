import uuid
from typing import Any
from sqlalchemy import ForeignKey, event, select, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, declarative_mixin, declared_attr, relationship

@declarative_mixin
class TenantMixin:
    """
    Mixin that adds a tenant_id column and a relationship to the Tenant model.
    Replaces the Rails `BelongsToTenant` concern.
    """
    
    @declared_attr
    def tenant_id(cls) -> Mapped[uuid.UUID]:
        return mapped_column(
            PG_UUID(as_uuid=True),
            ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        )

    @declared_attr
    def tenant(cls) -> Mapped[Any]:
        # String reference to avoid circular imports
        return relationship("Tenant", backref=f"{cls.__tablename__}_records")


@declarative_mixin
class AuditableMixin:
    """
    Mixin that hooks into SQLAlchemy events (insert, update, delete)
    to automatically write to the AuditLog table.
    Replaces the Rails `Auditable` concern.
    """
    pass


def _log_audit_change(mapper, connection, target, action):
    # This is a placeholder for the actual auditing logic.
    # In a real FastAPI app, extracting `Current.user` and `Current.tenant`
    # requires context variables or passing session state.
    # For now, we stub the event listener.
    pass

event.listen(AuditableMixin, 'after_insert', lambda m, c, t: _log_audit_change(m, c, t, 'create'), propagate=True)
event.listen(AuditableMixin, 'after_update', lambda m, c, t: _log_audit_change(m, c, t, 'update'), propagate=True)
event.listen(AuditableMixin, 'after_delete', lambda m, c, t: _log_audit_change(m, c, t, 'destroy'), propagate=True)


def restrict_on_delete(parent_cls, child_cls, fk_column):
    """Register a before_delete event to emulate dependent: :restrict_with_error.

    Usage (at module level after class definitions):
        restrict_on_delete(Grade, Employee, Employee.grade_id)
        restrict_on_delete(Department, Employee, Employee.department_id)

    Raises ValueError if any child records exist.
    """
    col_name = fk_column.name if hasattr(fk_column, 'name') else fk_column

    @event.listens_for(parent_cls, "before_delete")
    def _check(mapper, connection, target, _child_cls=child_cls, _col=col_name):
        count = connection.execute(
            select(func.count()).select_from(_child_cls.__table__).where(
                _child_cls.__table__.c[_col] == target.id
            )
        ).scalar()
        if count > 0:
            raise ValueError(
                f"Cannot delete {parent_cls.__name__} with associated {_child_cls.__name__} records"
            )
