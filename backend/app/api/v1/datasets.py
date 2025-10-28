from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.dataset import Dataset
from app.schemas.common import Dataset as DatasetSchema, DatasetCreate, DatasetUpdate

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
