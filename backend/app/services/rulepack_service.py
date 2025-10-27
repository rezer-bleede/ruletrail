from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import uuid

import pandas as pd
import yaml
from sqlmodel import select
from sqlalchemy.orm import selectinload

from ..core.config import get_settings
from ..core.database import session_scope
from ..models.rulepack import RuleDefinition, RulePack, RulePackVersion
from ..schemas.rulepack import (
    RuleDefinitionCreate,
    RuleDefinitionUpdate,
    RulePackCreate,
    RulePackRead,
    RulePackVersionCreate,
    RulePackVersionRead,
    BulkRuleUpdateRequest,
    RuleDefinitionRead,
)
from ..utils.checksum import compute_checksum
from ..utils.datetime import utcnow
from .audit import record_audit_event


def _calculate_checksum(rules: List[RuleDefinitionCreate]) -> str:
    payload = [
        f"{rule.domain}|{rule.group_name}|{rule.rule_id}|{rule.severity}|{rule.message}|{sorted(rule.condition.items())}"
        for rule in rules
    ]
    return compute_checksum(payload)


def list_rulepacks(tenant_id: Optional[uuid.UUID] = None) -> List[RulePackRead]:
    with session_scope() as session:
        statement = select(RulePack).options(
            selectinload(RulePack.versions).selectinload(RulePackVersion.rules)
        )
        if tenant_id:
            statement = statement.where(RulePack.tenant_id == tenant_id)
        rulepacks = session.exec(statement).all()
        return [RulePackRead.model_validate(rp) for rp in rulepacks]


def create_or_update_rulepack(payload: RulePackCreate) -> RulePackRead:
    with session_scope() as session:
        rulepack = session.exec(
            select(RulePack).where(
                RulePack.tenant_id == payload.tenant_id,
                RulePack.name == payload.name,
            )
        ).first()
        if not rulepack:
            rulepack = RulePack(
                tenant_id=payload.tenant_id,
                name=payload.name,
                description=payload.description,
            )
            session.add(rulepack)
            session.commit()
            session.refresh(rulepack)

        checksum = _calculate_checksum(payload.version.rules)
        existing_version = session.exec(
            select(RulePackVersion).where(
                RulePackVersion.rulepack_id == rulepack.id,
                RulePackVersion.checksum == checksum,
            )
        ).first()
        if existing_version:
            return RulePackRead.from_orm(rulepack)

        version = RulePackVersion(
            rulepack_id=rulepack.id,
            version=payload.version.version,
            checksum=checksum,
            pack_metadata=payload.version.metadata,
            published=payload.version.published,
            source_filename=payload.version.source_filename,
        )
        session.add(version)
        session.flush()

        for rule_payload in payload.version.rules:
            rule = RuleDefinition(
                version_id=version.id,
                domain=rule_payload.domain,
                group_name=rule_payload.group_name,
                rule_id=rule_payload.rule_id,
                clause=rule_payload.clause,
                severity=rule_payload.severity,
                threshold=rule_payload.threshold,
                message=rule_payload.message,
                mappings=rule_payload.mappings,
                condition=rule_payload.condition,
            )
            session.add(rule)

        rulepack.updated_at = utcnow()
        session.commit()
        record_audit_event(
            actor="system",
            action="import_rulepack",
            target_type="rulepack",
            target_id=str(rulepack.id),
            metadata={"version": version.version, "source": version.source_filename},
        )
        refreshed = session.exec(
            select(RulePack)
            .where(RulePack.id == rulepack.id)
            .options(selectinload(RulePack.versions).selectinload(RulePackVersion.rules))
        ).one()
        return RulePackRead.model_validate(refreshed)


def publish_rulepack_version(version_id: uuid.UUID) -> RulePackVersionRead:
    with session_scope() as session:
        version = session.get(RulePackVersion, version_id)
        if not version:
            raise ValueError("Version not found")
        version.published = True
        session.add(version)
        session.commit()
        session.refresh(version)
        record_audit_event(
            actor="system",
            action="publish_rulepack",
            target_type="rulepack_version",
            target_id=str(version.id),
            metadata={"version": version.version},
        )
        return RulePackVersionRead.model_validate(version)


def diff_rulepack_versions(base_id: uuid.UUID, compare_id: uuid.UUID) -> Dict[str, List[str]]:
    with session_scope() as session:
        base_version = session.get(RulePackVersion, base_id)
        compare_version = session.get(RulePackVersion, compare_id)
        if not base_version or not compare_version:
            raise ValueError("Invalid version identifiers")
        base_rules = {rule.rule_id: rule for rule in base_version.rules}
        compare_rules = {rule.rule_id: rule for rule in compare_version.rules}
        added = [rid for rid in compare_rules if rid not in base_rules]
        removed = [rid for rid in base_rules if rid not in compare_rules]
        changed = []
        for rule_id, rule in compare_rules.items():
            if rule_id in base_rules:
                if rule.condition != base_rules[rule_id].condition or rule.message != base_rules[rule_id].message:
                    changed.append(rule_id)
        return {"added": added, "removed": removed, "changed": changed}


def create_rule(version_id: uuid.UUID, payload: RuleDefinitionCreate) -> RuleDefinitionRead:
    with session_scope() as session:
        version = session.get(RulePackVersion, version_id)
        if not version:
            raise ValueError("Version not found")
        rule = RuleDefinition(
            version_id=version_id,
            domain=payload.domain,
            group_name=payload.group_name,
            rule_id=payload.rule_id,
            clause=payload.clause,
            severity=payload.severity,
            threshold=payload.threshold,
            message=payload.message,
            mappings=payload.mappings,
            condition=payload.condition,
            enabled=payload.enabled,
        )
        session.add(rule)
        session.commit()
        session.refresh(rule)
        record_audit_event(
            actor="system",
            action="create_rule",
            target_type="rule_definition",
            target_id=str(rule.id),
            metadata={"version_id": str(version_id)},
        )
        return RuleDefinitionRead.model_validate(rule)


def update_rule(rule_id: uuid.UUID, payload: RuleDefinitionUpdate) -> RuleDefinitionRead:
    with session_scope() as session:
        rule = session.get(RuleDefinition, rule_id)
        if not rule:
            raise ValueError("Rule not found")
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(rule, field, value)
        session.add(rule)
        session.commit()
        session.refresh(rule)
        record_audit_event(
            actor="system",
            action="update_rule",
            target_type="rule_definition",
            target_id=str(rule.id),
            metadata={"rule_id": rule.rule_id},
        )
        return RuleDefinitionRead.model_validate(rule)


def delete_rule(rule_id: uuid.UUID) -> None:
    with session_scope() as session:
        rule = session.get(RuleDefinition, rule_id)
        if not rule:
            raise ValueError("Rule not found")
        session.delete(rule)
        session.commit()
        record_audit_event(
            actor="system",
            action="delete_rule",
            target_type="rule_definition",
            target_id=str(rule_id),
            metadata={},
        )


def bulk_update_rules(version_id: uuid.UUID, request: BulkRuleUpdateRequest) -> List[RuleDefinitionRead]:
    with session_scope() as session:
        rules = session.exec(
            select(RuleDefinition).where(
                RuleDefinition.version_id == version_id,
                RuleDefinition.id.in_(request.rule_ids),
            )
        ).all()
        if not rules:
            return []
        for rule in rules:
            if request.action == "enable":
                rule.enabled = True
            elif request.action == "disable":
                rule.enabled = False
            elif request.action == "set_severity" and request.value:
                rule.severity = request.value
            elif request.action == "set_threshold" and request.value:
                rule.threshold = request.value
        session.commit()
        for rule in rules:
            session.refresh(rule)
        record_audit_event(
            actor="system",
            action="bulk_update_rules",
            target_type="rulepack_version",
            target_id=str(version_id),
            metadata={"action": request.action, "count": len(rules)},
        )
        return [RuleDefinitionRead.model_validate(rule) for rule in rules]


def export_rulepack_version(version_id: uuid.UUID) -> Dict[str, str]:
    settings = get_settings()
    storage = Path(settings.storage_path)
    storage.mkdir(parents=True, exist_ok=True)
    with session_scope() as session:
        version = session.exec(
            select(RulePackVersion)
            .where(RulePackVersion.id == version_id)
            .options(selectinload(RulePackVersion.rules))
        ).one()
        rows = []
        for rule in version.rules:
            row = {
                "Domain": rule.domain,
                "Group": rule.group_name,
                "Rule ID": rule.rule_id,
                "Clause": rule.clause,
                "Severity": rule.severity,
                "Threshold": rule.threshold,
                "Message": rule.message,
                "Enabled": rule.enabled,
            }
            for label, mapping in rule.mappings.items():
                row[f"Mapping:{label}"] = mapping
            for field, condition in rule.condition.items():
                row[f"Condition:{field}"] = condition.get("value")
                row[f"Operator:{field}"] = condition.get("operator")
            rows.append(row)
        frame = pd.DataFrame(rows)
        excel_path = storage / f"rulepack_{version.version}.xlsx"
        frame.to_excel(excel_path, index=False)

        yaml_payload = {
            "version": version.version,
            "metadata": version.pack_metadata,
            "rules": rows,
        }
        yaml_path = storage / f"rulepack_{version.version}.yaml"
        yaml_path.write_text(yaml.safe_dump(yaml_payload), encoding="utf-8")

        return {
            "excel": str(excel_path),
            "yaml": str(yaml_path),
        }
