from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # App
    PROJECT_NAME: str = "Voice Agent API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # API Keys
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key")
    ELEVENLABS_API_KEY: str = Field(default="", description="ElevenLabs API key")

    # OpenAI Settings
    OPENAI_MODEL: str = "gpt-4o-mini"

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }


# Only create the settings instance when required API keys are available
# For testing, we'll create it in the tests themselves
settings = Settings()