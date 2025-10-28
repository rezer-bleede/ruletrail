import io

import pandas as pd

from app.models.rulepack import RulePack
from app.services.rulepack_service import load_rulepack_from_excel


def create_excel_bytes():
    df = pd.DataFrame(
        [
            {
                "S. No.": 1,
                "Rule No.": "HR-001",
                "New Rule Name": "Test Rule",
                "Rule Logic - Business": "Amount greater than 10",
                "Conditions AND OR": "amount > 10",
                "Original Fields": "amount",
            }
        ]
    )
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="HR", index=False)
    buffer.seek(0)
    return buffer.getvalue()


def test_load_rulepack_from_excel(db_session):
    excel_bytes = create_excel_bytes()
    rulepacks = load_rulepack_from_excel(db_session, excel_bytes)
    assert len(rulepacks) == 1
    rulepack = rulepacks[0]
    assert rulepack.domain == "HR"
    assert len(rulepack.rules) == 1
    rule = rulepack.rules[0]
    assert rule.new_rule_name == "Test Rule"
    assert rule.conditions[0]["field"] == "amount"


def test_load_rulepack_from_excel_is_idempotent(db_session):
    excel_bytes = create_excel_bytes()
    first_import = load_rulepack_from_excel(db_session, excel_bytes)
    assert len(first_import) == 1

    second_import = load_rulepack_from_excel(db_session, excel_bytes)
    assert len(second_import) == 1
    assert second_import[0].id == first_import[0].id

    total_rulepacks = db_session.query(RulePack).count()
    assert total_rulepacks == 1


def test_load_rulepack_from_excel_preserves_metadata(db_session):
    excel_bytes = create_excel_bytes()
    metadata = {"source": "unit-test"}

    rulepacks = load_rulepack_from_excel(db_session, excel_bytes, metadata=metadata)
    assert rulepacks[0].pack_metadata == metadata


def test_load_rulepack_from_excel_allows_simple_condition_lists(db_session):
    df = pd.DataFrame(
        [
            {
                "S. No.": 1,
                "Rule No.": "HR-002",
                "New Rule Name": "Flag based rule",
                "Conditions AND OR": "Condition1 and Condition2",
                "Original Fields": "Condition1, Condition2",
            }
        ]
    )
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="HR", index=False)
    buffer.seek(0)

    rulepacks = load_rulepack_from_excel(db_session, buffer.getvalue())

    assert len(rulepacks) == 1
    rule = rulepacks[0].rules[0]
    assert len(rule.conditions) == 2
    assert rule.conditions[0]["operator"] == "exists"
    assert rule.conditions[0]["connector"] == "AND"
