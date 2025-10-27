from datetime import datetime
import uuid
from sqlalchemy import Column
from typing import Dict

from sqlalchemy.types import JSON
from sqlmodel import Field, SQLModel

from ..utils.datetime import utcnow


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"
    __table_args__ = {"extend_existing": True}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    actor: str
    action: str
    target_type: str
    target_id: str
    details: Dict[str, str] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    created_at: datetime = Field(default_factory=utcnow)
