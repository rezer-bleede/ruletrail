import os
import sys
import tempfile
from pathlib import Path

import pytest

from sqlmodel import SQLModel

sys.path.append(str(Path(__file__).resolve().parents[2]))

from app.core import config, database


@pytest.fixture(autouse=True)
def _setup_test_db(monkeypatch):
    with tempfile.NamedTemporaryFile(suffix='.db') as tmp:
        monkeypatch.setenv('DATABASE_URL', f'sqlite:///{tmp.name}')
        storage_dir = tempfile.mkdtemp()
        monkeypatch.setenv('STORAGE_PATH', storage_dir)
        config.get_settings.cache_clear()
        database._engine = None
        engine = database.get_engine()
        SQLModel.metadata.create_all(engine)
        yield
        SQLModel.metadata.drop_all(engine)
        config.get_settings.cache_clear()
        database._engine = None
