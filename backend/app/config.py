from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://sentinel:sentinel@db:5432/sentinelscan"
    postgres_db: str = "sentinelscan"
    postgres_user: str = "sentinel"
    postgres_password: str = "sentinel"
    redis_url: str = "redis://redis:6379/0"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    nuclei_binary: str = "nuclei"
    nuclei_timeout_seconds: int = 300
    gemini_api_key: str | None = None
    nvd_api_key: str | None = None
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
