"""Shared SQLAlchemy declarative base class used across models."""
from __future__ import annotations

from sqlalchemy.orm import declarative_base


Base = declarative_base()

__all__ = ["Base"]
