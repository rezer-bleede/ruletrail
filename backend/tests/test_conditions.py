from app.schemas.common import ConditionClause
from app.utils.conditions import (
    ConditionParserError,
    evaluate_boolean_chain,
    evaluate_conditions,
    parse_conditions,
)


def test_parse_conditions_handles_semicolons():
    raw = "amount > 10; status == 'OPEN'"
    clauses = parse_conditions(raw)
    assert len(clauses) == 2
    assert clauses[0].field == "amount"
    assert clauses[1].value == "OPEN"


def test_parse_conditions_invalid_segment_raises():
    try:
        parse_conditions("not-a-valid")
    except ConditionParserError as exc:
        assert "Unable to parse" in str(exc)
    else:
        raise AssertionError("Expected ConditionParserError")


def test_evaluate_conditions_and_chain():
    clauses = [
        ConditionClause(field="amount", operator=">", value=10, connector="AND"),
        ConditionClause(field="status", operator="=", value="OPEN"),
    ]
    inputs = {"amount": 15, "status": "OPEN"}
    evaluated = evaluate_conditions(clauses, inputs)
    result = evaluate_boolean_chain(evaluated)
    assert result is True


def test_evaluate_conditions_or_chain():
    clauses = [
        ConditionClause(field="amount", operator=">", value=10, connector="OR"),
        ConditionClause(field="status", operator="=", value="CLOSED"),
    ]
    inputs = {"amount": 5, "status": "CLOSED"}
    evaluated = evaluate_conditions(clauses, inputs)
    assert evaluate_boolean_chain(evaluated) is True
