from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.dataset import Dataset
from app.services.rulepack_service import load_rulepack_from_excel
from app.utils.seeder import seed_elasticsearch

logger = logging.getLogger(__name__)


settings = get_settings()
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    await seed_data()


async def seed_data(db: Optional[Session] = None):
    created_session = False
    if db is None:
        db = SessionLocal()
        created_session = True
    try:
        if settings.seed_excel_path and Path(settings.seed_excel_path).exists():
            with open(settings.seed_excel_path, "rb") as f:
                load_rulepack_from_excel(db, f.read(), metadata={"source": "seed"})
        if settings.seed_dataset_path and Path(settings.seed_dataset_path).exists():
            import json

            data = json.loads(Path(settings.seed_dataset_path).read_text())
            for dataset in data:
                existing = db.query(Dataset).filter(Dataset.name == dataset["name"]).first()
                if not existing:
                    db.add(Dataset(**dataset))
            db.commit()
        if settings.seed_es_path and Path(settings.seed_es_path).exists():
            from elasticsearch import Elasticsearch

            es = Elasticsearch(settings.elasticsearch_host)
            seed_elasticsearch(es, Path(settings.seed_es_path))
    except Exception as exc:
        logger.exception("Failed to seed data: %s", exc)
    finally:
        if created_session and db:
            db.close()


@app.get("/")
def root():
    return {"message": "RuleTrail API"}
