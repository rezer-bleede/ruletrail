from datetime import datetime
from typing import Dict
from pydantic import BaseModel, ConfigDict
import uuid


class AuditLogRead(BaseModel):
    id: uuid.UUID
    actor: str
    action: str
    target_type: str
    target_id: str
    details: Dict[str, str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
