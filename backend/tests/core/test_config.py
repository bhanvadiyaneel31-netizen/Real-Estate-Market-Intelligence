"""
Unit tests for the configuration module.
"""

import os
from unittest import mock
from app.core.config import Settings


def test_settings_default_values() -> None:
    """
    Test that Settings loads default values if no custom env is set.
    """
    settings = Settings()
    # Basic check of defaults
    assert settings.app_name == "Real Estate Market Intelligence Platform"
    assert settings.environment == "development"
    assert settings.log_level == "INFO"
    assert settings.host == "127.0.0.1"
    assert settings.port == 8000


def test_settings_load_from_env() -> None:
    """
    Test that Settings correctly overrides defaults with environment variables.
    """
    mock_env = {
        "APP_NAME": "Test Platform",
        "ENVIRONMENT": "testing",
        "LOG_LEVEL": "DEBUG",
        "DATABASE_URL": "postgresql://test:test@localhost:5432/test_db",
        "HOST": "0.0.0.0",
        "PORT": "9000",
    }
    with mock.patch.dict(os.environ, mock_env):
        settings = Settings()
        assert settings.app_name == "Test Platform"
        assert settings.environment == "testing"
        assert settings.log_level == "DEBUG"
        assert settings.database_url == "postgresql://test:test@localhost:5432/test_db"
        assert settings.host == "0.0.0.0"
        assert settings.port == 9000


def test_settings_validation_failure() -> None:
    """
    Test that invalid configuration values raise a Pydantic ValidationError.
    """
    from pydantic import ValidationError
    import pytest

    mock_env = {
        "PORT": "not-an-integer",
    }
    with mock.patch.dict(os.environ, mock_env):
        with pytest.raises(ValidationError):
            Settings()
