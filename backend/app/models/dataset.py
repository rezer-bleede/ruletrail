from __future__ import annotations

from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, JSON, String

from app.db.base_class import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    host = Column(String, nullable=False)
    index_name = Column(String, nullable=False)
    query = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
