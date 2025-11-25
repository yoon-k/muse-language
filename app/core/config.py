"""
MUSE Language - Configuration
"""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정."""

    # App
    APP_NAME: str = "MUSE Language"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://localhost:5432/muse_language"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # AI Services
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"

    # Speech
    GOOGLE_CLOUD_CREDENTIALS: str = ""

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Supported Languages
    SUPPORTED_LANGUAGES: List[str] = ["en", "ja", "zh", "es", "fr", "ko"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
