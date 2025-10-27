from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

from ..schemas.rulepack import RuleDefinitionCreate, RulePackVersionCreate
from ..utils.checksum import compute_checksum
from ..utils.datetime import iso_timestamp, utcnow

REQUIRED_COLUMNS = {
    "domain",
    "group",
    "rule id",
    "severity",
    "message",
}


class ExcelImportError(Exception):
    pass


def _normalize_header(header: str) -> str:
    return header.strip().lower()


def _extract_dynamic_columns(row: pd.Series, prefix: str) -> Dict[str, str]:
    dynamic: Dict[str, str] = {}
    for column, value in row.items():
        if not isinstance(column, str):
            continue
        lower = column.lower()
        if lower.startswith(prefix):
            key = lower.split(":", 1)[1] if ":" in lower else lower[len(prefix):]
            if value is not None and value != "":
                dynamic[key.strip()] = str(value)
    return dynamic


def load_excel_rulepack(path: Path) -> Tuple[RulePackVersionCreate, str, Dict[str, str]]:
    try:
        excel = pd.ExcelFile(path)
    except Exception as exc:  # pragma: no cover - error path
        raise ExcelImportError(f"Failed to open Excel file: {exc}") from exc

    rules: List[RuleDefinitionCreate] = []
    metadata: Dict[str, str] = {
        "sheets": ",".join(excel.sheet_names),
        "imported_at": iso_timestamp(),
    }

    for sheet_name in excel.sheet_names:
        frame = excel.parse(sheet_name)
        if frame.empty:
            continue
        normalized = {_normalize_header(col): col for col in frame.columns}
        missing = [col for col in REQUIRED_COLUMNS if col not in normalized]
        if missing:
            raise ExcelImportError(
                f"Sheet '{sheet_name}' missing required columns: {', '.join(missing)}"
            )
        for _, row in frame.iterrows():
            domain = str(row[normalized["domain"]]).strip()
            group_name = str(row[normalized["group"]]).strip()
            rule_id = str(row[normalized["rule id"]]).strip()
            clause = str(row[normalized.get("clause", normalized["rule id"])]).strip() if "clause" in normalized else None
            severity = str(row[normalized["severity"]]).strip()
            message = str(row[normalized["message"]]).strip()
            threshold = str(row[normalized.get("threshold", normalized["severity"])]).strip() if "threshold" in normalized else None

            condition = _extract_dynamic_columns(row, "condition")
            mappings = _extract_dynamic_columns(row, "mapping")
            if not condition:
                raise ExcelImportError(
                    f"Row in '{sheet_name}' missing condition columns with prefix 'Condition'"
                )

            rules.append(
                RuleDefinitionCreate(
                    domain=domain,
                    group_name=group_name,
                    rule_id=rule_id,
                    clause=clause,
                    severity=severity,
                    threshold=threshold,
                    message=message,
                    mappings=mappings,
                    condition={
                        key: {"operator": "==", "value": value}
                        for key, value in condition.items()
                    },
                )
            )

    if not rules:
        raise ExcelImportError("Excel file contained no rules")

    checksum = compute_checksum(
        [
            f"{rule.domain}|{rule.group_name}|{rule.rule_id}|{rule.severity}|{rule.message}|{sorted(rule.condition.items())}"
            for rule in rules
        ]
    )

    version = RulePackVersionCreate(
        version=utcnow().strftime("%Y.%m.%d.%H%M%S"),
        metadata=metadata,
        source_filename=path.name,
        rules=rules,
    )
    return version, checksum, metadata
