from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    ticket_app_db_url: str
    pgvector_db_url: str
    embedding_model: str
    tiktoken_encoding_model: str
    openrouter_api_key: str
    embedding_size: int = 1536

    model_config = SettingsConfigDict(env_file=env_path, extra="allow")


@lru_cache
def get_settings() -> Settings:
    return Settings()
