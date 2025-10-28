from fastapi import APIRouter

from . import datasets, health, rulepacks, runs

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(rulepacks.router, prefix="/rulepacks", tags=["rulepacks"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
api_router.include_router(runs.router, prefix="/runs", tags=["runs"])
