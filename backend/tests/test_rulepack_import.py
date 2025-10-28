import io

import pandas as pd

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
