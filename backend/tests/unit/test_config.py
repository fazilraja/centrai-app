import pytest
import os
from unittest.mock import patch
from pydantic import ValidationError
from app.config import Settings


def test_settings_default_values():
    """Test that Settings has correct default values"""
    # Arrange & Act
    settings = Settings(
        OPENAI_API_KEY="test_openai_key",
        ELEVENLABS_API_KEY="test_elevenlabs_key"
    )

    # Assert
    assert settings.PROJECT_NAME == "Voice Agent API"
    assert settings.VERSION == "1.0.0"
    assert settings.DEBUG is False
    assert settings.OPENAI_MODEL == "gpt-4o-mini"
    assert settings.FRONTEND_URL == "http://localhost:3000"
    assert settings.LOG_LEVEL == "INFO"


def test_settings_from_env():
    """Test that Settings loads values from environment"""
    # Arrange
    env_vars = {
        "OPENAI_API_KEY": "env_openai_key",
        "ELEVENLABS_API_KEY": "env_elevenlabs_key",
        "OPENAI_MODEL": "gpt-4",
        "FRONTEND_URL": "https://example.com",
        "LOG_LEVEL": "DEBUG",
        "DEBUG": "true"
    }

    # Act & Assert
    with patch.dict(os.environ, env_vars):
        settings = Settings()

        assert settings.OPENAI_API_KEY == "env_openai_key"
        assert settings.ELEVENLABS_API_KEY == "env_elevenlabs_key"
        assert settings.OPENAI_MODEL == "gpt-4"
        assert settings.FRONTEND_URL == "https://example.com"
        assert settings.LOG_LEVEL == "DEBUG"
        assert settings.DEBUG is True


def test_settings_default_api_keys():
    """Test that Settings has default empty API keys"""
    # Arrange & Act
    settings = Settings()

    # Assert
    assert settings.OPENAI_API_KEY == ""
    assert settings.ELEVENLABS_API_KEY == ""


def test_settings_instance():
    """Test that settings instance is accessible"""
    # Arrange & Act
    from app.config import settings

    # Assert
    assert isinstance(settings, Settings)


@patch.dict(os.environ, {
    "OPENAI_API_KEY": "test_key",
    "ELEVENLABS_API_KEY": "test_elevenlabs"
})
def test_settings_env_file_loading():
    """Test that settings can load from .env file"""
    # Arrange & Act
    settings = Settings()

    # Assert
    assert settings.OPENAI_API_KEY == "test_key"
    assert settings.ELEVENLABS_API_KEY == "test_elevenlabs"