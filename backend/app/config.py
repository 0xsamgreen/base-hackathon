from pydantic import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "db"  # Use the service name from docker-compose
    POSTGRES_PORT: str = "5432"  # Default PostgreSQL port

    @property
    def DATABASE_URL(self) -> str:
        """Generate the PostgreSQL connection URL."""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = "../.env"


@lru_cache()
def get_settings() -> Settings:
    """Create and cache settings instance."""
    return Settings()
