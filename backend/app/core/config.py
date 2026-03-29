from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATABASE_PATH = PROJECT_ROOT / "storage" / "app.db"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "OnboardAI API"
    database_url: str = Field(default=f"sqlite:///{DEFAULT_DATABASE_PATH.as_posix()}")
    jwt_secret_key: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 120
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    llm_request_timeout_seconds: float = 30.0


settings = Settings()
