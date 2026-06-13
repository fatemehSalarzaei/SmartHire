from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SmartHire"
    environment: str = "local"
    app_timezone: str = "Asia/Tehran"
    app_version: str = "0.1.0"
    log_level: str = "INFO"
    backend_cors_origins: str = "http://localhost:3000"
    database_url: str = "postgresql+psycopg://smarthire:change_me@postgres:5432/smarthire"
    redis_url: str = "redis://redis:6379/0"
    celery_broker_url: str = "redis://redis:6379/1"
    celery_result_backend: str = "redis://redis:6379/2"
    mask_sensitive_logs: bool = True
    enable_sqladmin: bool = True
    sqladmin_path: str = "/admin"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
