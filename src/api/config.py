"""API server configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the FastAPI server."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "nyc_taxi"
    postgres_user: str = "taxi_user"
    # Dev default only — must be overridden via .env in production deployments
    postgres_password: str = "taxi_pass"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 2

    cors_origins: str = "http://localhost:3000"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
