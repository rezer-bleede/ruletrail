from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Dict, List, Tuple

from elasticsearch import Elasticsearch
from sqlalchemy.orm import Session

from app.models.dataset import Dataset
from app.models.rulepack import Rule
from app.models.run import DecisionTrace, Run, RunRuleResult
from app.schemas.common import ConditionClause
from app.utils.conditions import evaluate_boolean_chain, evaluate_conditions

DEFAULT_LABELS = {
    "pass": "PASS",
    "fail": "FAIL",
    "warn": "WARN",
    "na": "N/A",
}


class EvaluationService:
    def __init__(self, db: Session, es_client: Elasticsearch):
        self.db = db
        self.es = es_client

    def run(self, domain: str, rulepack_id: int, dataset_id: int, status_labels: Dict[str, str] | None = None) -> Run:
        status_labels = status_labels or DEFAULT_LABELS
        rulepack = self._get_rulepack(rulepack_id)
        dataset = self.db.query(Dataset).filter(Dataset.id == dataset_id).one()
        snapshot = {
            "host": dataset.host,
            "index": dataset.index_name,
            "query": dataset.query,
        }
        run = Run(
            domain=domain,
            rulepack_id=rulepack.id,
            rulepack_checksum=rulepack.checksum,
            dataset_id=dataset.id,
            dataset_snapshot=snapshot,
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(run)
        self.db.flush()

        documents = self._fetch_documents(dataset)
        status_counter: Counter[str] = Counter()
        for rule in rulepack.rules:
            result, counter_update = self._evaluate_rule(rule, documents, status_labels)
            status_counter.update(counter_update)
            run_rule = RunRuleResult(
                run_id=run.id,
                rule_id=rule.id,
                status=result["status"],
                summary=result,
            )
            self.db.add(run_rule)
            for decision in result["decisions"]:
                trace = DecisionTrace(
                    rule_result=run_rule,
                    record_id=decision["record_id"],
                    status=decision["status"],
                    inputs=decision["inputs"],
                    clauses=decision["clauses"],
                    rationale=decision["rationale"],
                    extras=decision["extras"],
                )
                self.db.add(trace)

        run.status_counts = dict(status_counter)
        run.completed_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(run)
        return run

    def _get_rulepack(self, rulepack_id: int):
        from app.models.rulepack import RulePack

        rulepack = self.db.query(RulePack).filter(RulePack.id == rulepack_id).one()
        rulepack.rules  # ensure loaded
        return rulepack

    def _fetch_documents(self, dataset: Dataset) -> List[Dict]:
        query_body = dataset.query or {"query": {"match_all": {}}}
        if "query" not in query_body:
            query_body = {"query": query_body}
        response = self.es.search(
            index=dataset.index_name,
            body=query_body,
            size=1000,
        )
        hits = response.get("hits", {}).get("hits", [])
        return [{"_id": hit.get("_id"), **hit.get("_source", {})} for hit in hits]

    def _evaluate_rule(
        self,
        rule: Rule,
        documents: List[Dict],
        status_labels: Dict[str, str],
    ) -> Tuple[Dict[str, any], Counter[str]]:
        decisions: List[Dict[str, any]] = []
        counter: Counter[str] = Counter()
        clauses = [ConditionClause(**clause) for clause in (rule.conditions or [])]
        for doc in documents:
            inputs = {field: doc.get(field) for field in rule.original_fields or []}
            inputs.update({field: doc.get(field) for field in rule.aggregated_fields or []})
            evaluated_clauses = evaluate_conditions(clauses, doc)
            boolean_result = evaluate_boolean_chain(evaluated_clauses)
            status = status_labels["fail"] if boolean_result else status_labels["pass"]
            counter.update([status])
            rationale = self._build_rationale(rule, doc, evaluated_clauses, boolean_result, status_labels)
            decisions.append(
                {
                    "record_id": str(doc.get("_id", doc.get("id", "unknown"))),
                    "status": status,
                    "inputs": inputs,
                    "clauses": [
                        {
                            "field": ec.clause.field,
                            "operator": ec.clause.operator,
                            "value": ec.clause.value,
                            "connector": ec.clause.connector,
                            "result": ec.result,
                        }
                        for ec in evaluated_clauses
                    ],
                    "rationale": rationale,
                    "extras": {
                        "rule_no": rule.rule_no,
                        "new_rule_name": rule.new_rule_name,
                        "domain": rule.rulepack.domain if rule.rulepack else None,
                    },
                }
            )
        overall_status = status_labels["pass"]
        if counter.get(status_labels["fail"], 0) > 0:
            overall_status = status_labels["fail"]
        elif counter.get(status_labels["warn"], 0) > 0:
            overall_status = status_labels["warn"]
        summary = {
            "rule_id": rule.id,
            "rule_no": rule.rule_no,
            "new_rule_name": rule.new_rule_name,
            "status": overall_status,
            "decisions": decisions,
            "total_records": len(documents),
        }
        return summary, counter

    def _build_rationale(self, rule: Rule, doc: Dict, evaluated_clauses, boolean_result: bool, status_labels: Dict[str, str]) -> str:
        if not evaluated_clauses:
            return rule.rule_logic_business or "Rule evaluated without explicit clauses."
        failing = [ec for ec in evaluated_clauses if not ec.result]
        if boolean_result:
            clause = next((ec for ec in evaluated_clauses if ec.result), None)
            if clause:
                value = doc.get(clause.clause.field)
                return (
                    f"Because {clause.clause.field} value {value} satisfied {clause.clause.operator} {clause.clause.value}, "
                    f"the rule triggered and marked the record as {status_labels['fail']}."
                )
        else:
            clause = next((ec for ec in evaluated_clauses if not ec.result), None)
            if clause:
                value = doc.get(clause.clause.field)
                return (
                    f"Clause {clause.clause.field} value {value} did not satisfy {clause.clause.operator} {clause.clause.value}, "
                    f"so the record is considered {status_labels['pass']}."
                )
        clause = evaluated_clauses[0]
        value = doc.get(clause.clause.field)
        return f"{clause.clause.field} with value {value} maintained rule outcome {status_labels['pass'] if not boolean_result else status_labels['fail']}."
