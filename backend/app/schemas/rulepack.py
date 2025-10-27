from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
import uuid


class RuleDefinitionCreate(BaseModel):
    domain: str
    group_name: str
    rule_id: str
    clause: Optional[str]
    severity: str
    threshold: Optional[str]
    message: str
    mappings: Dict[str, str]
    condition: Dict[str, Dict[str, str]]
    enabled: bool = True


class RuleDefinitionUpdate(BaseModel):
    domain: Optional[str] = None
    group_name: Optional[str] = None
    clause: Optional[str] = None
    severity: Optional[str] = None
    threshold: Optional[str] = None
    message: Optional[str] = None
    mappings: Optional[Dict[str, str]] = None
    condition: Optional[Dict[str, Dict[str, str]]] = None
    enabled: Optional[bool] = None


class RulePackVersionCreate(BaseModel):
    version: str
    metadata: Dict[str, str] = Field(default_factory=dict)
    published: bool = False
    source_filename: Optional[str]
    rules: List[RuleDefinitionCreate]


class BulkRuleUpdateRequest(BaseModel):
    rule_ids: List[uuid.UUID]
    action: str
    value: Optional[str] = None


class RulePackCreate(BaseModel):
    tenant_id: uuid.UUID
    name: str
    description: Optional[str]
    version: RulePackVersionCreate


class RuleDefinitionRead(BaseModel):
    id: uuid.UUID
    domain: str
    group_name: str
    rule_id: str
    clause: Optional[str]
    severity: str
    threshold: Optional[str]
    message: str
    mappings: Dict[str, str]
    condition: Dict[str, Dict[str, str]]
    enabled: bool

    model_config = ConfigDict(from_attributes=True)


class RulePackVersionRead(BaseModel):
    id: uuid.UUID
    version: str
    imported_at: datetime
    checksum: str
    metadata: Dict[str, str] = Field(alias="pack_metadata")
    published: bool
    source_filename: Optional[str]
    rules: List[RuleDefinitionRead]

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class RulePackRead(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    versions: List[RulePackVersionRead]

    model_config = ConfigDict(from_attributes=True)
