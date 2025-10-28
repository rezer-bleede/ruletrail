from __future__ import annotations

from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.utils.seeder import seed_elasticsearch

from app.db.session import get_db
from app.models.dataset import Dataset
from app.schemas.common import Dataset as DatasetSchema, DatasetCreate, DatasetUpdate

try:  # pragma: no cover - optional dependency warning handled in runtime
    from elasticsearch import Elasticsearch
except ImportError:  # pragma: no cover - fallback for environments without ES client
    Elasticsearch = None  # type: ignore

router = APIRouter()


class ConnectionTestRequest(BaseModel):
    host: str


@router.get("/", response_model=List[DatasetSchema])
def list_datasets(db: Session = Depends(get_db)):
    datasets = db.query(Dataset).order_by(Dataset.created_at.desc()).all()
    return datasets


@router.post("/", response_model=DatasetSchema)
def create_dataset(dataset: DatasetCreate, db: Session = Depends(get_db)):
    dataset_db = Dataset(**dataset.dict())
    db.add(dataset_db)
    db.commit()
    db.refresh(dataset_db)
    return dataset_db


@router.put("/{dataset_id}", response_model=DatasetSchema)
def update_dataset(dataset_id: int, dataset: DatasetUpdate, db: Session = Depends(get_db)):
    dataset_db = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset_db:
        raise HTTPException(status_code=404, detail="Dataset not found")
    for key, value in dataset.dict().items():
        setattr(dataset_db, key, value)
    db.commit()
    db.refresh(dataset_db)
    return dataset_db


@router.delete("/{dataset_id}")
def delete_dataset(dataset_id: int, db: Session = Depends(get_db)):
    dataset_db = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset_db:
        raise HTTPException(status_code=404, detail="Dataset not found")
    db.delete(dataset_db)
    db.commit()
    return {"status": "deleted"}


@router.post("/test")
def test_connection(payload: ConnectionTestRequest):
    # For MVP we assume reachability; actual connectivity test requires network
    return {"host": payload.host, "status": "pending"}


@router.post("/seed-demo")
def seed_demo_data():
    settings = get_settings()
    seed_path = Path(settings.seed_es_path)
    if not seed_path.exists():
        raise HTTPException(status_code=404, detail="Demo seed file not found")
    if Elasticsearch is None:
        raise HTTPException(status_code=500, detail="Elasticsearch client is not installed")
    try:
        es = Elasticsearch(settings.elasticsearch_hosts)
    except Exception as exc:  # pragma: no cover - connection failures covered via integration test mocks
        raise HTTPException(status_code=503, detail=f"Failed to connect to Elasticsearch: {exc}") from exc
    indexed = seed_elasticsearch(es, seed_path)
    return {"indexed": indexed, "source": str(seed_path)}
