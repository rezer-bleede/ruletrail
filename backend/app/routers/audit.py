from fastapi import APIRouter
from sqlmodel import select

from ..core.database import session_scope
from ..models.audit import AuditLog
from ..schemas.audit import AuditLogRead

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/")
def list_audit_logs() -> list[AuditLogRead]:
    with session_scope() as session:
        logs = session.exec(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(200)).all()
        return [AuditLogRead.from_orm(log) for log in logs]
