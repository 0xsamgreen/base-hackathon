from pydantic import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    # Use SQLite database file in the project root
    DATABASE_URL: str = "sqlite:///./base-hackathon.db"
    TELEGRAM_BOT_TOKEN: str | None = None

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """Create and cache settings instance."""
    return Settings()
