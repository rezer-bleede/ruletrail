from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Run(Base):
    __tablename__ = "runs"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, nullable=False)
    rulepack_id = Column(Integer, ForeignKey("rulepacks.id"), nullable=False)
    rulepack_checksum = Column(String, nullable=False)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    dataset_snapshot = Column(JSON, nullable=False)
    status_counts = Column(JSON, default=dict)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime)

    rulepack = relationship("RulePack")
    dataset = relationship("Dataset")
    rule_results = relationship("RunRuleResult", back_populates="run", cascade="all, delete-orphan")


class RunRuleResult(Base):
    __tablename__ = "run_rule_results"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("runs.id", ondelete="CASCADE"), nullable=False)
    rule_id = Column(Integer, ForeignKey("rules.id"), nullable=False)
    status = Column(String, nullable=False)
    summary = Column(JSON, default=dict)

    run = relationship("Run", back_populates="rule_results")
    decisions = relationship("DecisionTrace", back_populates="rule_result", cascade="all, delete-orphan")


class DecisionTrace(Base):
    __tablename__ = "decision_traces"

    id = Column(Integer, primary_key=True, index=True)
    rule_result_id = Column(Integer, ForeignKey("run_rule_results.id", ondelete="CASCADE"), nullable=False)
    record_id = Column(String, nullable=False)
    status = Column(String, nullable=False)
    inputs = Column(JSON, default=dict)
    clauses = Column(JSON, default=list)
    rationale = Column(Text)
    extras = Column(JSON, default=dict)

    rule_result = relationship("RunRuleResult", back_populates="decisions")
