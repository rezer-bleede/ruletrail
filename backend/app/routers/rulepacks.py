from pathlib import Path
from typing import Optional
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from ..schemas.rulepack import (
    RuleDefinitionCreate,
    RuleDefinitionRead,
    RuleDefinitionUpdate,
    RulePackCreate,
    RulePackRead,
    RulePackVersionRead,
    BulkRuleUpdateRequest,
)
from ..services import excel_importer
from ..services.rulepack_service import (
    create_or_update_rulepack,
    create_rule,
    update_rule,
    delete_rule,
    bulk_update_rules,
    diff_rulepack_versions,
    list_rulepacks,
    publish_rulepack_version,
    export_rulepack_version,
)
from ..core.config import get_settings

router = APIRouter(prefix="/rulepacks", tags=["rulepacks"])


def _ensure_tempdir() -> Path:
    settings = get_settings()
    temp = Path(settings.storage_path) / "uploads"
    temp.mkdir(parents=True, exist_ok=True)
    return temp


@router.get("/")
def get_rulepacks(tenant_id: Optional[uuid.UUID] = None) -> list[RulePackRead]:
    return list_rulepacks(tenant_id)


@router.post("/import", response_model=RulePackRead)
async def import_rulepack(
    tenant_id: uuid.UUID,
    name: str,
    description: Optional[str] = None,
    file: UploadFile = File(...),
):
    tempdir = _ensure_tempdir()
    path = tempdir / file.filename
    path.write_bytes(await file.read())
    try:
        version, checksum, metadata = excel_importer.load_excel_rulepack(path)
    except excel_importer.ExcelImportError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    payload = RulePackCreate(
        tenant_id=tenant_id,
        name=name,
        description=description,
        version=version,
    )
    result = create_or_update_rulepack(payload)
    return result


@router.post("/{version_id}/publish", response_model=RulePackVersionRead)
def publish_version(version_id: uuid.UUID):
    return publish_rulepack_version(version_id)


@router.get("/diff")
def diff_versions(base_id: uuid.UUID, compare_id: uuid.UUID):
    return diff_rulepack_versions(base_id, compare_id)


@router.post("/{version_id}/rules", response_model=RuleDefinitionRead)
def create_rule_endpoint(version_id: uuid.UUID, payload: RuleDefinitionCreate):
    return create_rule(version_id, payload)


@router.put("/rules/{rule_id}", response_model=RuleDefinitionRead)
def update_rule_endpoint(rule_id: uuid.UUID, payload: RuleDefinitionUpdate):
    return update_rule(rule_id, payload)


@router.delete("/rules/{rule_id}")
def delete_rule_endpoint(rule_id: uuid.UUID):
    delete_rule(rule_id)
    return {"status": "deleted"}


@router.post("/{version_id}/rules/bulk", response_model=list[RuleDefinitionRead])
def bulk_update_rules_endpoint(version_id: uuid.UUID, request: BulkRuleUpdateRequest):
    return bulk_update_rules(version_id, request)


@router.get("/{version_id}/export")
def export_rulepack(version_id: uuid.UUID):
    return export_rulepack_version(version_id)
