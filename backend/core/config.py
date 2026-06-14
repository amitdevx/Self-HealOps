from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "SelfHealOps API"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    CORS_ORIGINS: list[str] = ["*"]  # Override in production .env

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/selfhealops"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # Security
    SECRET_KEY: str = "replace-with-a-very-secure-random-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # GitHub
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_WEBHOOK_SECRET: Optional[str] = None
    GITHUB_REPO: str = ""

    # AI
    NVIDIA_API_KEY: Optional[str] = None
    NIM_MODEL: str = "meta/llama3-70b-instruct"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore")

settings = Settings()
