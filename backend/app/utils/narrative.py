from typing import Optional

from ..models.rulepack import RuleDefinition


def build_narrative(rule: RuleDefinition, decision: str, affected_records: int) -> str:
    base = f"Rule {rule.rule_id} ({rule.severity}) - {rule.message}."
    if decision == "PASS":
        return base + " No records breached the configured thresholds."
    severity_text = "triggered" if affected_records else "evaluated"
    return (
        f"{base} The rule {severity_text} with {affected_records} record(s) failing the condition. "
        f"Threshold reference: {rule.threshold or 'n/a'}."
    )
