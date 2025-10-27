from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict
import uuid


class RecordEvaluationRead(BaseModel):
    id: uuid.UUID
    entity_id: str
    inputs: Dict[str, str]
    thresholds: Dict[str, str]
    decision: str
    trace: Dict[str, Dict[str, str]]

    model_config = ConfigDict(from_attributes=True)


class RuleEvaluationResultRead(BaseModel):
    id: uuid.UUID
    rule_id: uuid.UUID
    decision: str
    affected_records: int
    severity: str
    narrative: str
    trace: Dict[str, Dict[str, str]]
    records: List[RecordEvaluationRead]

    model_config = ConfigDict(from_attributes=True)


class EvaluationRunRead(BaseModel):
    id: uuid.UUID
    rulepack_version_id: uuid.UUID
    elasticsearch_index: str
    filters: Dict[str, str]
    started_at: datetime
    completed_at: Optional[datetime]
    status: str
    created_by: Optional[str]
    results: List[RuleEvaluationResultRead]

    model_config = ConfigDict(from_attributes=True)


class RunCreate(BaseModel):
    rulepack_version_id: uuid.UUID
    elasticsearch_index: str
    filters: Dict[str, str]
    created_by: Optional[str]
