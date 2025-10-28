import io

import pandas as pd

from app.models.dataset import Dataset
from app.services.evaluation_service import EvaluationService
from app.services.rulepack_service import load_rulepack_from_excel
from backend.tests.conftest import FakeElasticsearch


def build_rulepack(db_session):
    df = pd.DataFrame(
        [
            {
                "S. No.": 1,
                "Rule No.": "HR-001",
                "New Rule Name": "Overtime Alert",
                "Conditions AND OR": "overtime_hours > 40",
                "Original Fields": "overtime_hours",
            }
        ]
    )
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="HR", index=False)
    buffer.seek(0)
    rulepacks = load_rulepack_from_excel(db_session, buffer.getvalue())
    return rulepacks[0]


def test_evaluation_run(db_session):
    rulepack = build_rulepack(db_session)
    dataset = Dataset(name="test", host="http://mock", index_name="hr", query={"query": {"match_all": {}}})
    db_session.add(dataset)
    db_session.commit()
    es = FakeElasticsearch(
        [
            {"_id": "1", "overtime_hours": 45},
            {"_id": "2", "overtime_hours": 30},
        ]
    )
    service = EvaluationService(db_session, es)
    run = service.run("HR", rulepack.id, dataset.id)
    assert run.status_counts
    rule_result = run.rule_results[0]
    statuses = {trace.status for trace in rule_result.decisions}
    assert "FAIL" in statuses
    assert "PASS" in statuses
