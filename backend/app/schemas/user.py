from datetime import datetime
from pydantic import BaseModel, ConfigDict
import uuid


class UserCreate(BaseModel):
    email: str
    full_name: str
    role: str = "viewer"


class UserRead(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
