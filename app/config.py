from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Policy Data Reconciliation Assistant"
    app_env: str = "local"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
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
