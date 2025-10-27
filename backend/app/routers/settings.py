from fastapi import APIRouter

from ..core.config import get_settings
from ..services.es_client import es_provider

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/config")
def read_config():
    settings = get_settings()
    return {
        "app_name": settings.app_name,
        "environment": settings.environment,
        "elasticsearch_index": settings.elasticsearch_index,
        "feature_ai_assist_enabled": settings.feature_ai_assist_enabled,
    }


@router.get("/elasticsearch")
def test_elasticsearch(index: str | None = None):
    settings = get_settings()
    index_name = index or settings.elasticsearch_index
    return es_provider.test_connection(index_name)
