from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from io import BytesIO
from typing import Dict, List, Optional, Tuple

import pandas as pd
from sqlalchemy.orm import Session

from app.models.rulepack import Rule, RulePack
from app.schemas.common import ConditionClause
from app.utils.conditions import parse_conditions

COLUMN_MAP = {
    "Rule No.": "rule_no",
    "Rule No": "rule_no",
    "New Rule Name": "new_rule_name",
    "Sub Vertical": "sub_vertical",
    "ADAA Auditors STATUS": "adaa_auditors_status",
    "ADAA STATUS": "adaa_status",
    "UAEAA STATUS": "uaeaa_status",
    "Model": "model",
    "Test / Analysis": "test_analysis",
    "DE_RuleName": "de_rule_name",
    "BI_RuleName": "bi_rule_name",
    "Rule Objective": "rule_objective",
    "Rule Logic - Business": "rule_logic_business",
    "DE Rule Logic": "de_rule_logic",
    "UAEAA Rule Logic - DM": "uaeaa_rule_logic_dm",
    "UAEAA Comments": "uaeaa_comments",
    "ADAA Logic Implemented": "adaa_logic_implemented",
    "When / why to perform the test": "when_to_perform",
    "Interpreting the results": "interpreting_results",
    "Original Fields": "original_fields",
    "Aggregated or Calculated Fields": "aggregated_fields",
    "DM Comments": "dm_comments",
    "SingleEntites/Multi Entities": "single_entities",
    "EM Comments": "em_comments",
    "Action for Team": "action_for_team",
    "Final approval": "final_approval",
    "Dependency (Vertical & Columns)": "dependency",
    "Conditions AND OR": "conditions",
    "Rule Description": "rule_description",
}

LIST_COLUMNS = {"Original Fields", "Aggregated or Calculated Fields"}


def _clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={col: col.strip() for col in df.columns if isinstance(col, str)})
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    return df


def load_rulepack_from_excel(db: Session, file_bytes: bytes, metadata: Optional[Dict[str, str]] = None) -> List[RulePack]:
    checksum = hashlib.sha256(file_bytes).hexdigest()
    existing = db.query(RulePack).filter(RulePack.checksum == checksum).first()
    if existing:
        return [existing]

    excel = pd.ExcelFile(BytesIO(file_bytes))
    rulepacks: List[RulePack] = []
    for sheet_name in excel.sheet_names:
        df = excel.parse(sheet_name)
        df = _clean_columns(df)
        rules: List[Rule] = []
        for idx, row in df.iterrows():
            if row.dropna().empty:
                continue
            rule_data, extra_fields = _map_row_to_rule(row)
            clauses = rule_data.pop("conditions", [])
            rule = Rule(
                order_index=int(row.get("S. No.", idx + 1)),
                **rule_data,
                conditions=[clause.dict() for clause in clauses],
                extra=extra_fields,
            )
            rules.append(rule)
        if not rules:
            continue
        latest_version = (
            db.query(RulePack)
            .filter(RulePack.domain == sheet_name)
            .order_by(RulePack.version.desc())
            .first()
        )
        version = latest_version.version + 1 if latest_version else 1
        rulepack = RulePack(
            domain=sheet_name,
            version=version,
            checksum=checksum,
            uploaded_at=datetime.now(timezone.utc),
            pack_metadata=metadata or {},
            rules=rules,
        )
        db.add(rulepack)
        rulepacks.append(rulepack)
    db.commit()
    for rp in rulepacks:
        db.refresh(rp)
    return rulepacks


def _map_row_to_rule(row: pd.Series) -> Tuple[Dict[str, any], Dict[str, any]]:
    rule_data: Dict[str, any] = {}
    extra_fields: Dict[str, any] = {}
    for col, value in row.items():
        if pd.isna(value):
            continue
        normalized = COLUMN_MAP.get(col, None)
        if normalized == "conditions":
            clauses = parse_conditions(str(value))
            rule_data["conditions"] = clauses
        elif normalized in {"original_fields", "aggregated_fields"}:
            if isinstance(value, str):
                items = [item.strip() for item in re_split(value) if item.strip()]
            elif isinstance(value, list):
                items = value
            else:
                items = [value]
            rule_data[normalized] = items
        elif normalized:
            rule_data[normalized] = value
        else:
            extra_fields[col] = value
    if "rule_no" not in rule_data:
        rule_data["rule_no"] = str(row.name)
    if "new_rule_name" not in rule_data or not rule_data["new_rule_name"]:
        fallback_name = rule_data.get("de_rule_name") or rule_data.get("bi_rule_name") or f"Rule {row.name}"
        rule_data["new_rule_name"] = fallback_name
    return rule_data, extra_fields


def re_split(value: str) -> List[str]:
    return [segment.strip() for segment in re.split(r"[,;\n]", value)]
