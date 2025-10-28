from functools import lru_cache
from pydantic import BaseSettings, Field
from typing import List


class Settings(BaseSettings):
    app_name: str = "RuleTrail"
    backend_cors_origins: List[str] = Field(default_factory=lambda: ["*"])
    database_url: str = Field(default="sqlite:///./ruletrail.db")
    elasticsearch_host: str = Field(default="http://elasticsearch:9200")
    seed_excel_path: str = Field(default="backend/data/seed_rulepack.xlsx")
    seed_dataset_path: str = Field(default="backend/data/datasets.json")
    run_export_dir: str = Field(default="backend/data/exports")
    seed_es_path: str = Field(default="backend/data/es_seed.json")

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
