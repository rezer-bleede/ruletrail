from datetime import datetime
from typing import Dict, Optional
from sqlalchemy import Column
from sqlalchemy.types import JSON
from sqlmodel import Field, Relationship, SQLModel
import uuid

from ..utils.datetime import utcnow


class Tenant(SQLModel, table=True):
    __tablename__ = "tenants"
    __table_args__ = {"extend_existing": True}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str = Field(index=True)
    created_at: datetime = Field(default_factory=utcnow)

    rulepacks: list["RulePack"] = Relationship(back_populates="tenant")


class RulePack(SQLModel, table=True):
    __tablename__ = "rulepacks"
    __table_args__ = {"extend_existing": True}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id")
    name: str = Field(index=True)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    tenant: Tenant = Relationship(back_populates="rulepacks")
    versions: list["RulePackVersion"] = Relationship(back_populates="rulepack")


class RulePackVersion(SQLModel, table=True):
    __tablename__ = "rulepack_versions"
    __table_args__ = {"extend_existing": True}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    rulepack_id: uuid.UUID = Field(foreign_key="rulepacks.id")
    version: str = Field(index=True)
    imported_at: datetime = Field(default_factory=utcnow)
    checksum: str = Field(index=True)
    pack_metadata: Dict[str, str] = Field(
        default_factory=dict, sa_column=Column(JSON, nullable=False)
    )
    published: bool = Field(default=False)
    source_filename: Optional[str] = None

    rulepack: RulePack = Relationship(back_populates="versions")
    rules: list["RuleDefinition"] = Relationship(back_populates="version")
    runs: list["EvaluationRun"] = Relationship(back_populates="rulepack_version")


class RuleDefinition(SQLModel, table=True):
    __tablename__ = "rule_definitions"
    __table_args__ = {"extend_existing": True}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    version_id: uuid.UUID = Field(foreign_key="rulepack_versions.id")
    domain: str
    group_name: str
    rule_id: str
    clause: Optional[str] = None
    severity: str
    threshold: Optional[str] = None
    message: str
    mappings: Dict[str, str] = Field(
        default_factory=dict, sa_column=Column(JSON, nullable=False)
    )
    condition: Dict[str, Dict[str, str]] = Field(
        default_factory=dict, sa_column=Column(JSON, nullable=False)
    )
    enabled: bool = Field(default=True)

    version: RulePackVersion = Relationship(back_populates="rules")
