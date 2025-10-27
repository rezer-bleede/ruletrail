import io
import uuid

import pandas as pd
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.database import get_engine
from app.main import app
from app.models.rulepack import Tenant
from app.services import evaluation


def _ensure_tenant():
    engine = get_engine()
    with Session(engine) as session:
        tenant = session.exec(select(Tenant)).first()
        if not tenant:
            tenant = Tenant(id=uuid.uuid4(), name='Integration Tenant')
            session.add(tenant)
            session.commit()
            session.refresh(tenant)
        return tenant.id


def test_full_flow(monkeypatch):
    tenant_id = _ensure_tenant()

    df = pd.DataFrame(
        {
            'Domain': ['AML'],
            'Group': ['Risk'],
            'Rule ID': ['AML-42'],
            'Severity': ['High'],
            'Message': ['Flag transactions'],
            'Condition:transaction.amount': ['10000'],
        }
    )
    file_obj = io.BytesIO()
    df.to_excel(file_obj, index=False)
    file_obj.seek(0)

    with TestClient(app) as client:
        response = client.post(
            '/rulepacks/import',
            params={'tenant_id': str(tenant_id), 'name': 'Integration Pack'},
            files={'file': ('rules.xlsx', file_obj.getvalue(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')},
        )
        assert response.status_code == 200
        version_id = response.json()['versions'][0]['id']

        documents = [{'_source': {'id': 'abc', 'transaction': {'amount': 10000}}}]
        monkeypatch.setattr(evaluation.es_provider, 'scan', lambda index, query: documents)

        run_response = client.post(
            '/runs/',
            json={
                'rulepack_version_id': version_id,
                'elasticsearch_index': 'ruletrail-demo',
                'filters': {'status': 'active'},
                'created_by': 'integration',
            },
        )
        assert run_response.status_code == 200
        run_id = run_response.json()['run_id']

        details = client.get(f'/runs/{run_id}')
        assert details.status_code == 200
        payload = details.json()
        assert payload['results'][0]['affected_records'] >= 0

        export = client.post(f'/runs/{run_id}/export')
        assert export.status_code == 200
        assert 'artifacts' in export.json()
