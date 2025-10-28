from __future__ import annotations

import operator
import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

from app.schemas.common import ConditionClause


def _value_is_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) > 0
    return True


_OPERATORS: Dict[str, Callable[[Any, Any], bool]] = {
    "==": operator.eq,
    "=": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
    "contains": lambda a, b: b in a if a is not None else False,
    "not_contains": lambda a, b: b not in a if a is not None else True,
    "exists": lambda value, expected: _value_is_present(value) if expected else not _value_is_present(value),
}

_CONDITION_PATTERN = re.compile(
    r"^\s*(?P<field>[\w.\s]+?)\s*(?P<operator>>=|<=|!=|==|=|>|<|contains)\s*(?P<value>.+?)\s*$",
    re.IGNORECASE,
)

_SIMPLE_FIELD_PATTERN = re.compile(r"^\s*(?P<field>[\w.\s\-]+?)\s*$")

_CONNECTOR_PATTERN = re.compile(r"\b(AND|OR)\b", re.IGNORECASE)


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
    for segment, connector in _split_into_segments(raw_value):
        clause = _parse_segment(segment, connector)
        clauses.append(clause)
    return clauses


def _split_into_segments(raw_value: str) -> Iterable[Tuple[str, Optional[str]]]:
    normalized = re.sub(r"[\r\n;]+", " AND ", raw_value)
    tokens = [token for token in _CONNECTOR_PATTERN.split(normalized) if token and token.strip()]
    segments: List[Tuple[str, Optional[str]]] = []
    for token in tokens:
        token_stripped = token.strip()
        if _CONNECTOR_PATTERN.fullmatch(token_stripped):
            if segments:
                last_segment, _ = segments[-1]
                segments[-1] = (last_segment, token_stripped.upper())
            continue
        segments.append((token_stripped, None))
    return segments


def _parse_segment(segment: str, connector: Optional[str]) -> ConditionClause:
    text = segment.strip()
    if not text:
        raise ConditionParserError("Empty condition segment")

    negated = False
    if text.upper().startswith("NOT "):
        negated = True
        text = text[4:].strip()

    match = _CONDITION_PATTERN.match(text)
    if match:
        field = match.group("field").strip()
        operator_symbol = match.group("operator").lower()
        value_str = match.group("value").strip()
        value = _normalize_value(value_str)
        if negated:
            operator_symbol, value = _negate_operator(operator_symbol, value)
        return ConditionClause(field=field, operator=operator_symbol, value=value, connector=connector)

    simple_match = _SIMPLE_FIELD_PATTERN.match(text)
    if simple_match:
        field = simple_match.group("field").strip()
        if not field:
            raise ConditionParserError("Condition field cannot be empty")
        expected = not negated
        return ConditionClause(field=field, operator="exists", value=expected, connector=connector)

    raise ConditionParserError(f"Unable to parse condition segment: '{segment}'")


def _negate_operator(operator_symbol: str, value: Any) -> Tuple[str, Any]:
    mapping = {
        "==": "!=",
        "=": "!=",
        "!=": "=",
        ">": "<=",
        ">=": "<",
        "<": ">=",
        "<=": ">",
        "contains": "not_contains",
    }
    negated = mapping.get(operator_symbol, operator_symbol)
    return negated, value


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
