from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List

import yaml
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.models.run import Run, RunRuleResult
from app.schemas.common import Run as RunSchema, RunRuleResultSchema, RunSummary
from app.schemas.run_requests import RunExportRequest, StartRunRequest
from app.services.evaluation_service import EvaluationService

router = APIRouter()


@router.get("/", response_model=List[RunSummary])
def list_runs(db: Session = Depends(get_db)):
    runs = db.query(Run).order_by(Run.started_at.desc()).all()
    return [RunSummary.from_orm(run) for run in runs]


@router.post("/start", response_model=RunSchema)
def start_run(payload: StartRunRequest, db: Session = Depends(get_db)):
    from elasticsearch import Elasticsearch

    settings = get_settings()
    from app.models.dataset import Dataset

    dataset = db.query(Dataset).filter(Dataset.id == payload.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    hosts = [dataset.host] if dataset.host else settings.elasticsearch_hosts
    es = Elasticsearch(hosts)
    service = EvaluationService(db, es)
    run = service.run(payload.domain, payload.rulepack_id, payload.dataset_id, payload.status_labels)
    return run


@router.get("/{run_id}", response_model=RunSchema)
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.get("/{run_id}/rules", response_model=List[RunRuleResultSchema])
def get_run_rule_results(run_id: int, db: Session = Depends(get_db)):
    run_results = db.query(RunRuleResult).filter(RunRuleResult.run_id == run_id).all()
    return run_results


@router.get("/{run_id}/decisions", response_model=List[RunRuleResultSchema])
def get_run_decisions(run_id: int, db: Session = Depends(get_db)):
    run_results = (
        db.query(RunRuleResult).filter(RunRuleResult.run_id == run_id).all()
    )
    return run_results


@router.post("/{run_id}/export")
def export_run(run_id: int, payload: RunExportRequest, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    settings = get_settings()
    export_dir = Path(settings.run_export_dir)
    export_dir.mkdir(parents=True, exist_ok=True)
    data = RunSchema.from_orm(run).dict()
    if payload.format == "json":
        export_path = export_dir / f"run_{run_id}.json"
        export_path.write_text(json.dumps(data, indent=2, default=str))
    else:
        export_path = export_dir / f"run_{run_id}.yaml"
        export_path.write_text(yaml.safe_dump(data))
    return {"path": str(export_path)}
