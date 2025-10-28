import io

import pandas as pd
from fastapi.testclient import TestClient

from app.services.rulepack_service import load_rulepack_from_excel
from app.services import evaluation_service
from backend.tests.conftest import FakeElasticsearch


def prepare_rulepack_bytes():
    df = pd.DataFrame(
        [
            {
                "S. No.": 1,
                "Rule No.": "HR-010",
                "New Rule Name": "API Rule",
                "Conditions AND OR": "score > 5",
                "Original Fields": "score",
            }
        ]
    )
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="HR", index=False)
    buffer.seek(0)
    return buffer.getvalue()


def test_rule_crud_and_run(client, db_session):
    excel_bytes = prepare_rulepack_bytes()
    response = client.post("/api/rulepacks/import", files={"file": ("rules.xlsx", excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert response.status_code == 200
    rulepacks = response.json()
    rulepack_id = rulepacks[0]["id"]

    rule_data = {
        "order_index": 1,
        "rule_no": "HR-011",
        "new_rule_name": "API Rule 2",
        "conditions": [],
    }
    create_resp = client.post(f"/api/rulepacks/{rulepack_id}/rules", json=rule_data)
    assert create_resp.status_code == 200
    rule_id = create_resp.json()["id"]

    update_payload = {**rule_data, "new_rule_name": "Updated"}
    update_resp = client.put(f"/api/rulepacks/rules/{rule_id}", json=update_payload)
    assert update_resp.status_code == 200
    assert update_resp.json()["new_rule_name"] == "Updated"

    dataset_payload = {
        "name": "API Dataset",
        "host": "http://mock:9200",
        "index_name": "api_index",
        "query": {"query": {"match_all": {}}},
    }
    dataset_resp = client.post("/api/datasets/", json=dataset_payload)
    assert dataset_resp.status_code == 200
    dataset_id = dataset_resp.json()["id"]

    fake_es = FakeElasticsearch([
        {"_id": "1", "score": 6},
        {"_id": "2", "score": 3},
    ])

    def _fake_es_client(*args, **kwargs):
        return fake_es

    evaluation_service.Elasticsearch = _fake_es_client  # type: ignore
    from app.api.v1 import runs as runs_module
    import elasticsearch

    runs_module.Elasticsearch = _fake_es_client  # type: ignore
    elasticsearch.Elasticsearch = _fake_es_client  # type: ignore

    run_payload = {
        "domain": "HR",
        "rulepack_id": rulepack_id,
        "dataset_id": dataset_id,
    }
    run_resp = client.post("/api/runs/start", json=run_payload)
    assert run_resp.status_code == 200
    run_data = run_resp.json()
    assert run_data["status_counts"]


def test_rulepack_import_includes_filename_metadata(client):
    excel_bytes = prepare_rulepack_bytes()
    filename = "hr-rules.xlsx"

    response = client.post(
        "/api/rulepacks/import",
        files={"file": (filename, excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert response.status_code == 200
    rulepack_id = response.json()[0]["id"]

    detail_resp = client.get(f"/api/rulepacks/{rulepack_id}")
    assert detail_resp.status_code == 200
    payload = detail_resp.json()
    assert payload["pack_metadata"]["filename"] == filename
