from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    ticket_app_db_url: str

    model_config = SettingsConfigDict(env_file=env_path, extra="allow")


@lru_cache
def get_settings() -> Settings:
    return Settings()
