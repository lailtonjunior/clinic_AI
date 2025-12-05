from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    app_name: str = "NexusClin"
    debug: bool = True
    database_url: str = "postgresql+psycopg2://nexus:nexus@db:5432/nexus"
    secret_key: str = "changeme"
    allowed_origins: List[str] = ["*"]
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
    seed_tenant_name: str | None = None
    seed_admin_email: str | None = None
    seed_admin_password: str | None = None
    seed_run_on_startup: bool = False
    cmd_job_enabled: bool = True
    cmd_job_interval_minutes: int = 1440

    class Config:
        env_file = ".env"


settings = Settings()
