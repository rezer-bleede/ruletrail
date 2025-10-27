import uuid

from fastapi import APIRouter, HTTPException

from ..schemas.run import EvaluationRunRead, RunCreate
from ..services.evaluation import execute_run, get_run_results
from ..services.exporter import export_run_artifacts

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("/", response_model=dict)
def start_run(payload: RunCreate):
    run_id = execute_run(payload)
    return {"run_id": run_id}


@router.get("/{run_id}", response_model=EvaluationRunRead)
def read_run(run_id: uuid.UUID):
    try:
        return get_run_results(run_id)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=404, detail="Run not found") from exc


@router.post("/{run_id}/export")
def export_run(run_id: uuid.UUID):
    run = get_run_results(run_id)
    payload = EvaluationRunRead.model_validate(run).model_dump(mode="json")
    artifacts = export_run_artifacts(payload)
    return {"artifacts": artifacts}
