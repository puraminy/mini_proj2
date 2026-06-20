import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the API service."""

    app_name: str = "Mini Project 2 API"
    database_url: str = "sqlite:///./mini_proj2.db"


@lru_cache
def get_settings() -> Settings:
    return Settings(database_url=os.getenv("DATABASE_URL", Settings.database_url))
