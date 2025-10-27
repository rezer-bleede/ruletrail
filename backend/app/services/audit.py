from contextlib import contextmanager
from typing import Dict

from sqlmodel import Session

from ..core.database import session_scope
from ..models.audit import AuditLog


@contextmanager
def audit_session():
    with session_scope() as session:
        yield session


def record_audit_event(actor: str, action: str, target_type: str, target_id: str, metadata: Dict):
    with audit_session() as session:
        event = AuditLog(
            actor=actor,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=metadata,
        )
        session.add(event)
        session.commit()
