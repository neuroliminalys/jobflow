from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_path: str
    debug: bool
    cors_allowed_origins: list[str]
    n8n_cv_webhook_url: str | None = None
    n8n_job_applications_webhook_url: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
