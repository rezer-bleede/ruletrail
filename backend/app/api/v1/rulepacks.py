from __future__ import annotations

from typing import List

from fastapi import Depends, File, HTTPException, UploadFile
from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.rulepack import Rule, RulePack
from app.schemas.common import Rule as RuleSchema
from app.schemas.common import RuleCreate, RulePack as RulePackSchema, RulePackList, RuleUpdate
from app.services.rulepack_service import RulepackImportError, load_rulepack_from_excel

router = APIRouter()


@router.post("/import", response_model=List[RulePackList])
async def import_rulepacks(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    try:
        rulepacks = load_rulepack_from_excel(db, contents, metadata={"filename": file.filename})
    except RulepackImportError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return [RulePackList.from_orm(rp) for rp in rulepacks]


@router.get("/", response_model=List[RulePackList])
def list_rulepacks(db: Session = Depends(get_db)):
    rulepacks = db.query(RulePack).order_by(RulePack.domain, RulePack.version.desc()).all()
    return rulepacks


@router.get("/{rulepack_id}", response_model=RulePackSchema)
def get_rulepack(rulepack_id: int, db: Session = Depends(get_db)):
    rulepack = db.query(RulePack).filter(RulePack.id == rulepack_id).first()
    if not rulepack:
        raise HTTPException(status_code=404, detail="Rulepack not found")
    return rulepack


@router.get("/{rulepack_id}/rules", response_model=List[RuleSchema])
def list_rules(rulepack_id: int, db: Session = Depends(get_db)):
    rules = db.query(Rule).filter(Rule.rulepack_id == rulepack_id).order_by(Rule.order_index).all()
    return rules


@router.post("/{rulepack_id}/rules", response_model=RuleSchema)
def create_rule(rulepack_id: int, rule: RuleCreate, db: Session = Depends(get_db)):
    rulepack = db.query(RulePack).filter(RulePack.id == rulepack_id).first()
    if not rulepack:
        raise HTTPException(status_code=404, detail="Rulepack not found")
    rule_db = Rule(rulepack_id=rulepack_id, **rule.dict())
    db.add(rule_db)
    db.commit()
    db.refresh(rule_db)
    return rule_db


@router.put("/rules/{rule_id}", response_model=RuleSchema)
def update_rule(rule_id: int, rule: RuleUpdate, db: Session = Depends(get_db)):
    rule_db = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule_db:
        raise HTTPException(status_code=404, detail="Rule not found")
    for key, value in rule.dict().items():
        setattr(rule_db, key, value)
    db.commit()
    db.refresh(rule_db)
    return rule_db


@router.delete("/rules/{rule_id}")
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    rule_db = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule_db:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(rule_db)
    db.commit()
    return {"status": "deleted"}
