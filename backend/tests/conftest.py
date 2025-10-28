from __future__ import annotations

import io
import sys
from pathlib import Path
from typing import Dict, List

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parent
for candidate in (str(ROOT), str(PROJECT_ROOT)):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

import app.compat  # noqa: F401
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.core.config import Settings
from app.db.base import Base
from app.main import app, seed_data

TEST_DB_URL = "sqlite:///:memory:"


def override_settings() -> Settings:
    settings = Settings()
    settings.database_url = TEST_DB_URL
    settings.seed_excel_path = ""
    settings.seed_dataset_path = ""
    return settings


def create_test_engine():
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="function")
def db_session(monkeypatch):
    engine = create_test_engine()
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    from app.db import session as session_module
    from app.core import config as config_module

    test_settings = Settings(
        database_url=TEST_DB_URL,
        seed_excel_path="",
        seed_dataset_path="",
        run_export_dir="./exports",
        seed_es_path="",
        elasticsearch_host="http://mock-es"
    )

    if hasattr(config_module.get_settings, "cache_clear"):
        config_module.get_settings.cache_clear()

    def _get_settings():
        return test_settings

    monkeypatch.setattr(session_module, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(session_module, "engine", engine)
    monkeypatch.setattr(config_module, "get_settings", _get_settings)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session, monkeypatch):
    Base.metadata.drop_all(bind=db_session.get_bind())
    Base.metadata.create_all(bind=db_session.get_bind())
    from app.db import session as session_module

    def _get_db():
        try:
            yield db_session
        finally:
            pass

    monkeypatch.setattr(session_module, "get_db", _get_db)
    yield TestClient(app)


class FakeElasticsearch:
    def __init__(self, documents: List[Dict]):
        self.documents = documents

    def search(self, index: str, body: Dict, size: int = 1000):
        return {
            "hits": {
                "hits": [
                    {"_id": doc.get("_id", str(idx)), "_source": doc}
                    for idx, doc in enumerate(self.documents)
                ]
            }
        }


@pytest.fixture
async def seeded_data(db_session, monkeypatch):
    Base.metadata.create_all(bind=db_session.get_bind())
    await seed_data(db_session)
    yield db_session
