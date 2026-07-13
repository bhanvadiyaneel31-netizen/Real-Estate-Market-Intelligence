"""
Configuration management module for loading and validating environment variables.
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables and .env file.
    """
    app_name: str = "Real Estate Market Intelligence Platform"
    environment: str = "development"
    log_level: str = "INFO"
    database_url: str = "postgresql://postgres:postgres@localhost:5432/real_estate"
    host: str = "127.0.0.1"
    port: int = 8000

    # Locate the .env file in the backend/ directory relative to this config file.
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Instantiate settings
settings = Settings()
