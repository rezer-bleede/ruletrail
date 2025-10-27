import uuid
from sqlmodel import Session

from app.core.database import get_engine
from app.models.rulepack import RulePack, RulePackVersion, Tenant
from app.schemas.rulepack import RuleDefinitionCreate, RuleDefinitionUpdate, BulkRuleUpdateRequest
from app.services import rulepack_service


def _bootstrap(session: Session):
    tenant = Tenant(id=uuid.uuid4(), name='Tenant')
    session.add(tenant)
    session.commit()
    session.refresh(tenant)
    pack = RulePack(tenant_id=tenant.id, name='Pack', description='desc')
    session.add(pack)
    session.commit()
    session.refresh(pack)
    version = RulePackVersion(rulepack_id=pack.id, version='v1', checksum='abc', pack_metadata={}, published=False)
    session.add(version)
    session.commit()
    session.refresh(version)
    return version.id


def test_rule_crud_flow():
    engine = get_engine()
    with Session(engine) as session:
        version_id = _bootstrap(session)

    created = rulepack_service.create_rule(
        version_id,
        RuleDefinitionCreate(
            domain='AML',
            group_name='Risk',
            rule_id='R1',
            clause='1',
            severity='High',
            threshold='1000',
            message='Test',
            mappings={'amount': 'transaction.amount'},
            condition={'transaction.amount': {'operator': '>', 'value': '1000'}},
        ),
    )
    assert created.rule_id == 'R1'

    updated = rulepack_service.update_rule(created.id, RuleDefinitionUpdate(severity='Low'))
    assert updated.severity == 'Low'

    rulepack_service.bulk_update_rules(
        version_id,
        BulkRuleUpdateRequest(rule_ids=[created.id], action='set_threshold', value='2000'),
    )
    exported = rulepack_service.export_rulepack_version(version_id)
    assert 'excel' in exported and 'yaml' in exported

    rulepack_service.delete_rule(created.id)
