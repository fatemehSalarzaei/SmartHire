from functools import lru_cache

from pydantic import Field
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
    jwt_secret_key: str = "change_me_very_long_random"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    kando_ats_base_url: str = "https://atsedgeapi.hrcando.ir"
    kando_basedata_base_url: str = "https://basedataapinew.hrcando.ir"
    kando_company_api_key: str = Field(
        default="replace_with_secret",
        validation_alias="KANDO_API_KEY",
    )
    kando_company_api_header_name: str = Field(
        default="CompanyApiKey",
        validation_alias="KANDO_API_HEADER_KEY",
    )
    kando_request_timeout_seconds: float = Field(
        default=30.0,
        validation_alias="KANDO_TIMEOUT_SECONDS",
    )
    kando_page_size: int = Field(default=100, validation_alias="KANDO_DEFAULT_PAGE_SIZE")
    kando_max_retries: int = 3

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
