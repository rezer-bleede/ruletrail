from fastapi import APIRouter

from ..core.config import get_settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/ready")
def readiness():
    settings = get_settings()
    return {"status": "ok", "environment": settings.environment}


@router.get("/live")
def liveness():
    return {"status": "alive"}
