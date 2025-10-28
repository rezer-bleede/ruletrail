from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class RulePack(Base):
    __tablename__ = "rulepacks"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, index=True, nullable=False)
    version = Column(Integer, nullable=False)
    checksum = Column(String, nullable=False, index=True)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    pack_metadata = Column(JSON, default=dict)

    rules = relationship("Rule", back_populates="rulepack", cascade="all, delete-orphan")



class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    rulepack_id = Column(Integer, ForeignKey("rulepacks.id", ondelete="CASCADE"), nullable=False)
    order_index = Column(Integer, nullable=False, default=0)
    rule_no = Column(String, nullable=False)
    new_rule_name = Column(String, nullable=False)
    sub_vertical = Column(String)
    adaa_auditors_status = Column(String)
    adaa_status = Column(String)
    uaeaa_status = Column(String)
    model = Column(String)
    test_analysis = Column(String)
    de_rule_name = Column(String)
    bi_rule_name = Column(String)
    rule_objective = Column(Text)
    rule_logic_business = Column(Text)
    de_rule_logic = Column(Text)
    uaeaa_rule_logic_dm = Column(Text)
    uaeaa_comments = Column(Text)
    adaa_logic_implemented = Column(Text)
    when_to_perform = Column(Text)
    interpreting_results = Column(Text)
    original_fields = Column(JSON, default=list)
    aggregated_fields = Column(JSON, default=list)
    dm_comments = Column(Text)
    single_entities = Column(String)
    em_comments = Column(Text)
    action_for_team = Column(Text)
    final_approval = Column(Text)
    dependency = Column(Text)
    conditions = Column(JSON, default=list)
    extra = Column(JSON, default=dict)

    rulepack = relationship("RulePack", back_populates="rules")
