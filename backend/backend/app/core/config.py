"""
app/core/config.py

Loads configuration from environment variables (or a .env file when present).
All settings have sensible development defaults so the app runs out-of-the-box
without a .env file being present.

Usage anywhere in the application:
    from app.core.config import settings
    print(settings.app_env)
"""

from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    """
    Application settings.
    Values are read from environment variables first; a .env file is loaded
    as a fallback if python-dotenv is available (installed via pydantic-settings).
    """

    # General
    app_env: str = "development"

    # CORS — comma-separated string in the env var, parsed into a list below
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ]
    
    # Database
    database_url: str = "sqlite:///./coolblock.db"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> List[str]:
        """
        Accept either a comma-separated string (from an env var) or a list
        (from a Python default / test override).
        """
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.
    The cache means the .env file is only read once per process.
    Call get_settings.cache_clear() in tests when you need a fresh instance.
    """
    return Settings()


# Module-level convenience alias used throughout the app
settings = get_settings()
