from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class ConditionClause(BaseModel):
    field: str
    operator: str
    value: Any
    connector: Optional[str] = None


class RuleBase(BaseModel):
    order_index: int = 0
    rule_no: str
    new_rule_name: str
    sub_vertical: Optional[str] = None
    adaa_auditors_status: Optional[str] = None
    adaa_status: Optional[str] = None
    uaeaa_status: Optional[str] = None
    model: Optional[str] = None
    test_analysis: Optional[str] = None
    de_rule_name: Optional[str] = None
    bi_rule_name: Optional[str] = None
    rule_objective: Optional[str] = None
    rule_logic_business: Optional[str] = None
    de_rule_logic: Optional[str] = None
    uaeaa_rule_logic_dm: Optional[str] = None
    uaeaa_comments: Optional[str] = None
    adaa_logic_implemented: Optional[str] = None
    when_to_perform: Optional[str] = None
    interpreting_results: Optional[str] = None
    original_fields: List[str] = []
    aggregated_fields: List[str] = []
    dm_comments: Optional[str] = None
    single_entities: Optional[str] = None
    em_comments: Optional[str] = None
    action_for_team: Optional[str] = None
    final_approval: Optional[str] = None
    dependency: Optional[str] = None
    conditions: List[ConditionClause] = []
    extra: Dict[str, Any] = {}


class RuleCreate(RuleBase):
    pass


class RuleUpdate(RuleBase):
    pass


class Rule(RuleBase):
    id: int

    class Config:
        orm_mode = True


class RulePackBase(BaseModel):
    domain: str
    version: int
    checksum: str
    uploaded_at: datetime
    pack_metadata: Dict[str, Any] = {}


class RulePack(RulePackBase):
    id: int
    rules: List[Rule] = []

    class Config:
        orm_mode = True


class RulePackList(BaseModel):
    id: int
    domain: str
    version: int
    checksum: str
    uploaded_at: datetime

    class Config:
        orm_mode = True


class DatasetBase(BaseModel):
    name: str
    host: str
    index_name: str
    query: Dict[str, Any] = {}


class DatasetCreate(DatasetBase):
    pass


class DatasetUpdate(DatasetBase):
    pass


class Dataset(DatasetBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class RunBase(BaseModel):
    domain: str
    rulepack_id: int
    dataset_id: int
    rulepack_checksum: str
    dataset_snapshot: Dict[str, Any]
    status_counts: Dict[str, int] = {}
    started_at: datetime
    completed_at: Optional[datetime] = None


class DecisionTraceSchema(BaseModel):
    id: int
    record_id: str
    status: str
    inputs: Dict[str, Any]
    clauses: List[Dict[str, Any]]
    rationale: Optional[str]

    class Config:
        orm_mode = True


class RunRuleResultSchema(BaseModel):
    id: int
    rule_id: int
    status: str
    summary: Dict[str, Any]
    decisions: List[DecisionTraceSchema]

    class Config:
        orm_mode = True


class Run(RunBase):
    id: int
    rule_results: List[RunRuleResultSchema] = []

    class Config:
        orm_mode = True


class RunSummary(BaseModel):
    id: int
    domain: str
    status_counts: Dict[str, int]
    started_at: datetime
    completed_at: Optional[datetime]
