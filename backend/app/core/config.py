from functools import lru_cache
import json
from typing import List

from pydantic import BaseSettings, Field, root_validator, validator


DEFAULT_ELASTICSEARCH_HOST = "http://elasticsearch:9200"


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
