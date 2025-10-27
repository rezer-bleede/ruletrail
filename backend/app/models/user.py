from datetime import datetime
import uuid
from sqlmodel import Field, SQLModel

from ..utils.datetime import utcnow

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    full_name: str
    role: str = Field(default="viewer")
    created_at: datetime = Field(default_factory=utcnow)
