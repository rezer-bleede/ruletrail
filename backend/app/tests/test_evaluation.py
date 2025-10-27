import uuid
from sqlmodel import Session

from app.models.rulepack import RuleDefinition, RulePack, RulePackVersion, Tenant
from app.services.evaluation import execute_run, get_run_results
from app.schemas.run import RunCreate
from app.services import evaluation
from app.core.database import get_engine


def _setup_rulepack(session: Session):
    tenant = Tenant(id=uuid.uuid4(), name='Demo Tenant')
    session.add(tenant)
    session.commit()
    session.refresh(tenant)

    rulepack = RulePack(tenant_id=tenant.id, name='Demo', description='Demo pack')
    session.add(rulepack)
    session.commit()
    session.refresh(rulepack)

    version = RulePackVersion(
        rulepack_id=rulepack.id,
        version='v1',
        checksum='123',
        pack_metadata={},
        published=True,
    )
    session.add(version)
    session.commit()
    session.refresh(version)

    rule = RuleDefinition(
        version_id=version.id,
        domain='AML',
        group_name='Risk',
        rule_id='AML-1',
        clause='1.1',
        severity='High',
        threshold='> 10000',
        message='High value transactions',
        mappings={'transaction.amount': 'transaction.amount'},
        condition={'transaction.amount': {'operator': '>', 'value': '10000'}},
        enabled=True,
    )
    session.add(rule)
    session.commit()
    return version.id


def test_execute_run(monkeypatch):
    engine = get_engine()
    with Session(engine) as session:
        version_id = _setup_rulepack(session)

    documents = [
        {'_source': {'id': '1', 'transaction': {'amount': 15000}}},
        {'_source': {'id': '2', 'transaction': {'amount': 5000}}},
    ]

    monkeypatch.setattr(evaluation.es_provider, 'scan', lambda index, query: documents)

    run_id = execute_run(
        RunCreate(
            rulepack_version_id=version_id,
            elasticsearch_index='demo',
            filters={'status': 'active'},
            created_by='tester',
        )
    )

    run = get_run_results(run_id)
    assert run.status == 'completed'
    assert run.results[0].affected_records == 1
    record = run.results[0].records[0]
    assert record.entity_id == '1'
    assert 'transaction.amount' in record.trace
