from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Policy Data Reconciliation Assistant"
    app_env: str = "local"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    mock_llm: bool = True
    cache_dir: Path = Path(".cache/llm_extractions")
    input_dir: Path = Path("sample_data")
    output_dir: Path = Path("outputs")
    max_input_tokens: int = Field(default=12000, gt=0)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
