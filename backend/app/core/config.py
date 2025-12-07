import secrets
from typing import List, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "NexusClin"
    environment: Literal["dev", "staging", "prod"] = "dev"
    debug: bool = False
    database_url: str = "postgresql+psycopg2://nexus:nexus@db:5432/nexus"
    secret_key: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32)
    )  # Generated when not provided to avoid weak defaults
    allowed_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000"]
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    s3_endpoint: str = "http://minio:9000"
    s3_access_key: str = "minio"
    s3_secret_key: str = "minio123"
    s3_bucket: str = "nexusclin"
    redis_url: str = "redis://redis:6379/0"
    sigtap_base_url: str = "https://ftp.datasus.gov.br/dissemin/publicos/SIGTAP/200810_/TabelasUnificadas"
    sigtap_admin_token: str = "dev-admin-token"
    sigtap_job_enabled: bool = True
    sigtap_job_interval_hours: int = 24
    mfa_required: bool = False
    icp_brasil_enabled: bool = False
    seed_tenant_name: str | None = None
    seed_admin_email: str | None = None
    seed_admin_password: str | None = None
    seed_run_on_startup: bool = False
    cmd_job_enabled: bool = True
    cmd_job_interval_minutes: int = 1440
    ai_api_key: str | None = None
    ai_model_name: str | None = None

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def split_allowed_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


settings = Settings()
