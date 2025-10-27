from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    app_name: str = "RuleTrail"
    environment: str = Field(default="development", alias="ENVIRONMENT")
    database_url: str = Field(default="sqlite:///./ruletrail.db", alias="DATABASE_URL")
    elasticsearch_hosts: List[str] = Field(default_factory=lambda: ["http://elasticsearch:9200"], alias="ELASTICSEARCH_HOSTS")
    elasticsearch_index: str = Field(default="ruletrail-demo", alias="ELASTICSEARCH_INDEX")
    feature_ai_assist_enabled: bool = Field(default=True, alias="FEATURE_AI_ASSIST_ENABLED")
    storage_path: str = Field(default="/data", alias="STORAGE_PATH")
    secret_key: str = Field(default="insecure-demo-secret", alias="SECRET_KEY")

    @field_validator("elasticsearch_hosts", mode="before")
    def _coerce_hosts(cls, value):
        if isinstance(value, str):
            return [host.strip() for host in value.split(",") if host]
        return value


@lru_cache()
def get_settings() -> Settings:
    return Settings()
