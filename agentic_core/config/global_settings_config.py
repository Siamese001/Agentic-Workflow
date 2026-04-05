# /agentic_core/config/settings.py
# Implementation of Singleton Settings using pydantic-settings
# Validation: Strict types, .env loading support

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from agentic_core.config.core.constants_config import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

# Configuration constants

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError as _err:
    raise ImportError(
        "pydantic-settings is required for this module. Install with: pip install -e '.[infra]'",
    ) from _err


class Settings(BaseSettings):
    """
    Global application configuration.
    Immutable after load.
    """

    # Core Application Settings
    APP_NAME: str = Field(default="AgenticCore", description="Application identifier")
    ENVIRONMENT: Literal["dev", "test", "prod"] = Field(default="dev", description="Runtime environment")
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Logging verbosity",
    )

    # Security / Secrets (Placeholder for future phases)
    API_KEY: SecretStr = Field(default=SecretStr(""), description="Master API Key (optional)")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Allow extra fields in .env without crashing
    )


@lru_cache
def get_settings() -> Settings:
    """
    Singleton accessor for Settings.
    Cached to prevent re-parsing .env on every call.
    """
    return Settings()
