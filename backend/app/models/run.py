from datetime import datetime
from typing import Dict, Optional
import uuid
from sqlalchemy import Column
from sqlalchemy.types import JSON
from sqlmodel import Field, Relationship, SQLModel

from ..utils.datetime import utcnow


class EvaluationRun(SQLModel, table=True):
    __tablename__ = "evaluation_runs"
    __table_args__ = {"extend_existing": True}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    rulepack_version_id: uuid.UUID = Field(foreign_key="rulepack_versions.id")
    elasticsearch_index: str
    filters: Dict[str, str] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    started_at: datetime = Field(default_factory=utcnow)
    completed_at: Optional[datetime] = None
    status: str = Field(default="pending")
    created_by: Optional[str] = None

    rulepack_version: "RulePackVersion" = Relationship(back_populates="runs")
    results: list["RuleEvaluationResult"] = Relationship(back_populates="run")


class RuleEvaluationResult(SQLModel, table=True):
    __tablename__ = "rule_evaluation_results"
    __table_args__ = {"extend_existing": True}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    run_id: uuid.UUID = Field(foreign_key="evaluation_runs.id")
    rule_id: uuid.UUID = Field(foreign_key="rule_definitions.id")
    decision: str
    affected_records: int = Field(default=0)
    severity: str
    narrative: str
    trace: Dict[str, Dict[str, str]] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))

    run: EvaluationRun = Relationship(back_populates="results")
    records: list["RecordEvaluation"] = Relationship(back_populates="result")


class RecordEvaluation(SQLModel, table=True):
    __tablename__ = "record_evaluations"
    __table_args__ = {"extend_existing": True}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    result_id: uuid.UUID = Field(foreign_key="rule_evaluation_results.id")
    entity_id: str
    inputs: Dict[str, str] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    thresholds: Dict[str, str] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    decision: str
    trace: Dict[str, Dict[str, str]] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))

    result: RuleEvaluationResult = Relationship(back_populates="records")
