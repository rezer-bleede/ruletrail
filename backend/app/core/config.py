from functools import lru_cache
import json
from typing import List

try:  # pragma: no cover - import fallback for pydantic v1
    from pydantic_settings import BaseSettings  # type: ignore[attr-defined]
except ImportError:  # pragma: no cover - runtime fallback when pydantic-settings is absent
    from pydantic import BaseSettings  # type: ignore[no-redef]

from pydantic import Field, root_validator, validator


DEFAULT_ELASTICSEARCH_HOST = "http://elasticsearch:9200"


def _safe_json_loads(value: str):
    """Gracefully decode JSON strings coming from environment variables.

    Pydantic's settings sources attempt to JSON-decode environment variables for
    complex fields. When an empty string (or otherwise invalid JSON) is provided
    we want to defer the interpretation to our validator instead of raising a
    ``JSONDecodeError``. Returning the original value allows the validator to
    apply our custom parsing rules.
    """

    if not isinstance(value, str):
        return value

    stripped = value.strip()
    if not stripped:
        return value

    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        return value


class Settings(BaseSettings):
    app_name: str = "RuleTrail"
    backend_cors_origins: List[str] = Field(default_factory=lambda: ["*"])
    database_url: str = Field(default="sqlite:///./ruletrail.db")
    elasticsearch_hosts: List[str] = Field(default_factory=lambda: [DEFAULT_ELASTICSEARCH_HOST])
    seed_excel_path: str = Field(default="backend/data/seed_rulepack.xlsx")
    seed_dataset_path: str = Field(default="backend/data/datasets.json")
    run_export_dir: str = Field(default="backend/data/exports")
    seed_es_path: str = Field(default="backend/data/es_seed.json")

    class Config:
        env_file = ".env"
        json_loads = staticmethod(_safe_json_loads)
        fields = {"elasticsearch_hosts": {"env": ["ELASTICSEARCH_HOSTS", "ELASTICSEARCH_HOST"]}}

        @classmethod
        def parse_env_var(cls, field_name: str, raw_value: str):
            if field_name == "elasticsearch_hosts":
                # Defer parsing to the validator so we can support plain strings
                return raw_value
            return super().parse_env_var(field_name, raw_value)

    @root_validator(pre=True)
    def _handle_legacy_host(cls, values):  # type: ignore[override]
        host = values.pop("elasticsearch_host", None)
        hosts = values.get("elasticsearch_hosts")
        if host and not hosts:
            values["elasticsearch_hosts"] = host
        return values

    @validator("elasticsearch_hosts", pre=True)
    def parse_elasticsearch_hosts(cls, value):  # type: ignore[override]
        if value in (None, "", [], ()):  # treat empty values as missing
            return [DEFAULT_ELASTICSEARCH_HOST]
        if isinstance(value, list):
            return value or [DEFAULT_ELASTICSEARCH_HOST]
        if isinstance(value, str):
            raw_value = value.strip()
            if not raw_value:
                return [DEFAULT_ELASTICSEARCH_HOST]
            try:
                decoded = json.loads(raw_value)
            except json.JSONDecodeError:
                decoded = None
            if isinstance(decoded, list):
                return [str(item) for item in decoded if str(item).strip()]
            # Fallback to comma separated values
            hosts = [item.strip() for item in raw_value.split(",") if item.strip()]
            return hosts or [DEFAULT_ELASTICSEARCH_HOST]
        return [DEFAULT_ELASTICSEARCH_HOST]

    @property
    def elasticsearch_host(self) -> str:
        """Return the primary Elasticsearch host for backwards compatibility."""

        return self.elasticsearch_hosts[0]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
