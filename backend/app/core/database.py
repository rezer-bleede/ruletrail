from contextlib import contextmanager
from typing import Iterator

from sqlmodel import SQLModel, Session, create_engine

from .config import get_settings


_engine = None


def get_engine():
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(settings.database_url, echo=False, future=True)
    return _engine


def init_db() -> None:
    SQLModel.metadata.create_all(bind=get_engine())


@contextmanager
def session_scope() -> Iterator[Session]:
    with Session(get_engine()) as session:
        yield session


def get_session() -> Session:
    return Session(get_engine())
