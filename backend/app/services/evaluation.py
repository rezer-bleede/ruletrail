from __future__ import annotations

from typing import Dict, Iterable, List, Tuple
import uuid

from sqlmodel import select
from sqlalchemy.orm import selectinload

from ..core.database import session_scope
from ..models.rulepack import RuleDefinition, RulePackVersion
from ..models.run import EvaluationRun, RecordEvaluation, RuleEvaluationResult
from ..schemas.run import RunCreate
from ..utils.datetime import utcnow
from ..utils.narrative import build_narrative
from .es_client import es_provider

DECISION_PASS = "PASS"
DECISION_FAIL = "FAIL"
DECISION_WARN = "WARN"
DECISION_NA = "NA"


def _match_condition(value, operator: str, expected: str) -> Tuple[bool, str]:
    if value is None:
        return False, f"Value missing; expected {operator} {expected}"
    if operator == "==":
        return value == expected, f"{value} == {expected}"
    if operator == "!=":
        return value != expected, f"{value} != {expected}"
    try:
        numeric_value = float(value)
        numeric_expected = float(expected)
    except (ValueError, TypeError):
        numeric_value = numeric_expected = None
    if operator == ">" and numeric_value is not None:
        return numeric_value > numeric_expected, f"{numeric_value} > {numeric_expected}"
    if operator == ">=" and numeric_value is not None:
        return numeric_value >= numeric_expected, f"{numeric_value} >= {numeric_expected}"
    if operator == "<" and numeric_value is not None:
        return numeric_value < numeric_expected, f"{numeric_value} < {numeric_expected}"
    if operator == "<=" and numeric_value is not None:
        return numeric_value <= numeric_expected, f"{numeric_value} <= {numeric_expected}"
    if operator == "contains":
        return expected in str(value), f"{expected} in {value}"
    if operator == "in":
        options = [opt.strip() for opt in expected.split(",")]
        return str(value) in options, f"{value} in {options}"
    if operator == "not_in":
        options = [opt.strip() for opt in expected.split(",")]
        return str(value) not in options, f"{value} not in {options}"
    return False, f"Unsupported operator {operator}"


def _get_nested_value(doc: Dict, path: str):
    parts = path.split(".")
    value = doc
    for part in parts:
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            return None
    return value


def _build_query(filters: Dict[str, str]) -> Dict:
    must = []
    for field, value in filters.items():
        must.append({"term": {field: value}})
    return {"query": {"bool": {"must": must}}} if must else {"query": {"match_all": {}}}


def _evaluate_rule(rule: RuleDefinition, doc: Dict) -> Tuple[str, Dict[str, Dict[str, str]]]:
    trace: Dict[str, Dict[str, str]] = {}
    matches = []
    for field, predicate in rule.condition.items():
        operator = predicate.get("operator", "==")
        expected = predicate.get("value")
        actual = _get_nested_value(doc, field)
        match, detail = _match_condition(actual, operator, expected)
        trace[field] = {
            "operator": operator,
            "expected": str(expected),
            "actual": "" if actual is None else str(actual),
            "detail": detail,
        }
        matches.append(match)
    decision = DECISION_FAIL if all(matches) else DECISION_PASS
    return decision, trace


def execute_run(run_data: RunCreate) -> uuid.UUID:
    with session_scope() as session:
        version = session.get(RulePackVersion, run_data.rulepack_version_id)
        if not version:
            raise ValueError("RulePack version not found")
        run = EvaluationRun(
            rulepack_version_id=version.id,
            elasticsearch_index=run_data.elasticsearch_index,
            filters=run_data.filters,
            status="running",
            created_by=run_data.created_by,
        )
        session.add(run)
        session.commit()
        session.refresh(run)

        docs = list(es_provider.scan(run.elasticsearch_index, _build_query(run.filters)))
        doc_sources = [doc.get("_source", {}) for doc in docs]

        results: List[RuleEvaluationResult] = []
        for rule in version.rules:
            if not rule.enabled:
                continue
            affected_records = []
            for source in doc_sources:
                decision, trace = _evaluate_rule(rule, source)
                if decision == DECISION_FAIL:
                    record = RecordEvaluation(
                        result_id=uuid.uuid4(),  # placeholder, replaced later
                        entity_id=str(source.get("id", source.get("_id", "unknown"))),
                        inputs={label: str(_get_nested_value(source, field)) for label, field in rule.mappings.items()},
                        thresholds={"threshold": rule.threshold or ""},
                        decision=decision,
                        trace=trace,
                    )
                    affected_records.append(record)
            overall_decision = DECISION_PASS if not affected_records else DECISION_FAIL
            narrative = build_narrative(
                rule=rule,
                decision=overall_decision,
                affected_records=len(affected_records),
            )
            result = RuleEvaluationResult(
                run_id=run.id,
                rule_id=rule.id,
                decision=overall_decision,
                affected_records=len(affected_records),
                severity=rule.severity,
                narrative=narrative,
                trace={
                    "rule": {
                        "domain": rule.domain,
                        "group": rule.group_name,
                        "message": rule.message,
                    }
                },
            )
            session.add(result)
            session.flush()
            for record in affected_records:
                record.result_id = result.id
                session.add(record)
            results.append(result)

        run.status = "completed"
        run.completed_at = utcnow()
        session.add(run)
        session.commit()
        return run.id


def get_run_results(run_id: uuid.UUID) -> EvaluationRun:
    with session_scope() as session:
        statement = (
            select(EvaluationRun)
            .where(EvaluationRun.id == run_id)
            .options(
                selectinload(EvaluationRun.results).selectinload(RuleEvaluationResult.records)
            )
        )
        run = session.exec(statement).one()
        return run
