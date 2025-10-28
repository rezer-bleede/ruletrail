from __future__ import annotations

import operator
import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List

from app.schemas.common import ConditionClause

_OPERATORS: Dict[str, Callable[[Any, Any], bool]] = {
    "==": operator.eq,
    "=": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
    "contains": lambda a, b: b in a if a is not None else False,
}

_CONDITION_PATTERN = re.compile(
    r"\s*(?P<field>[\w.]+)\s*(?P<operator>>=|<=|!=|==|=|>|<|contains)\s*(?P<value>.+?)\s*(?P<connector>AND|OR)?\s*$",
    re.IGNORECASE,
)


@dataclass
class EvaluatedClause:
    clause: ConditionClause
    result: bool


class ConditionParserError(ValueError):
    pass


def parse_conditions(raw_value: str) -> List[ConditionClause]:
    if not raw_value:
        return []

    clauses: List[ConditionClause] = []
    segments: Iterable[str]
    if "\n" in raw_value:
        segments = [s for s in raw_value.splitlines() if s.strip()]
    elif ";" in raw_value:
        segments = [s.strip() for s in raw_value.split(";") if s.strip()]
    else:
        segments = [raw_value]

    for segment in segments:
        match = _CONDITION_PATTERN.match(segment)
        if not match:
            raise ConditionParserError(f"Unable to parse condition segment: '{segment}'")
        field = match.group("field")
        operator_symbol = match.group("operator").lower()
        value_str = match.group("value").strip()
        connector = match.group("connector")
        if connector:
            connector = connector.upper()
        value = _normalize_value(value_str)
        clause = ConditionClause(field=field, operator=operator_symbol, value=value, connector=connector)
        clauses.append(clause)
    return clauses


def _normalize_value(value_str: str) -> Any:
    lower = value_str.lower()
    if lower in {"true", "false"}:
        return lower == "true"
    if lower in {"null", "none"}:
        return None
    if value_str.startswith("\"") and value_str.endswith("\""):
        return value_str.strip("\"")
    if value_str.startswith("'") and value_str.endswith("'"):
        return value_str.strip("'")
    try:
        if "." in value_str:
            return float(value_str)
        return int(value_str)
    except ValueError:
        return value_str


def evaluate_conditions(clauses: List[ConditionClause], inputs: Dict[str, Any]) -> List[EvaluatedClause]:
    evaluated: List[EvaluatedClause] = []
    for clause in clauses:
        value = _extract_input_value(inputs, clause.field)
        op = _OPERATORS.get(clause.operator.lower())
        if not op:
            raise ConditionParserError(f"Unsupported operator: {clause.operator}")
        try:
            result = op(value, clause.value)
        except Exception:
            result = False
        evaluated.append(EvaluatedClause(clause=clause, result=result))
    return evaluated


def _extract_input_value(inputs: Dict[str, Any], field: str) -> Any:
    if field in inputs:
        return inputs[field]
    if "." in field:
        current = inputs
        for part in field.split("."):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        return current
    return inputs.get(field)


def evaluate_boolean_chain(evaluated: List[EvaluatedClause]) -> bool:
    if not evaluated:
        return True
    result = evaluated[0].result
    for idx, clause in enumerate(evaluated[1:], start=1):
        connector = evaluated[idx - 1].clause.connector or "AND"
        if connector == "AND":
            result = result and clause.result
        elif connector == "OR":
            result = result or clause.result
        else:
            raise ConditionParserError(f"Unsupported connector: {connector}")
    return result
