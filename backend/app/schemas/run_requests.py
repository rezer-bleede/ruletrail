from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class StartRunRequest(BaseModel):
    domain: str
    rulepack_id: int
    dataset_id: int
    status_labels: Dict[str, str] = {
        "pass": "PASS",
        "fail": "FAIL",
        "warn": "WARN",
        "na": "N/A",
    }


class RunResultFilter(BaseModel):
    rule_id: Optional[int] = None
    status: Optional[str] = None
    page: int = 1
    size: int = 50


class RunExportRequest(BaseModel):
    include_decisions: bool = True
    format: str = "json"


class RunDecisionResponse(BaseModel):
    run_id: int
    rule_id: int
    record_id: str
    status: str
    rationale: Optional[str]
    inputs: Dict[str, Any]
    clauses: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    created_at: datetime
