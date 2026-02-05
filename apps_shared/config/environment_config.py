"""
Environment Variable Validation System.

Provides fail-fast environment validation for all required API keys and configuration.
Phase 2A.1 - Critical Infrastructure Foundation
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Final

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class EnvironmentConfig(BaseModel):
    """Environment configuration with validation for required API keys."""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        validate_default=True,
    )

    # Core LLM Providers (Required)
    OPENAI_API_KEY: str = Field(..., min_length=1, description="OpenAI API key")
    ANTHROPIC_API_KEY: str = Field(..., min_length=1, description="Anthropic API key")
    GEMINI_API_KEY: str = Field(..., min_length=1, description="Google Gemini API key")

    # Vector Database (Required)
    PINECONE_API_KEY: str = Field(..., min_length=1, description="Pinecone API key")

    # Redis Configuration (Required)
    REDIS_HOST: str = Field(default="localhost", description="Redis host")
    REDIS_PORT: int = Field(default=6379, description="Redis port")
    REDIS_URL: str = Field(default="redis://localhost:6379", description="Redis connection URL")

    # Optional Providers
    MISTRALAI_API_KEY: str | None = Field(default=None, description="Mistral AI API key")
    COHERE_API_KEY: str | None = Field(default=None, description="Cohere API key")
    GROQ_API_KEY: str | None = Field(default=None, description="Groq API key")
    TOGETHER_API_KEY: str | None = Field(default=None, description="Together AI API key")
    FIREWORKS_API_KEY: str | None = Field(default=None, description="Fireworks AI API key")
    BRAVE_SEARCH_API_KEY: str | None = Field(default=None, description="Brave Search API key")

    # GitHub & MCP Configuration
    GITHUB_TOKEN: str | None = Field(default=None, description="GitHub personal access token")
    DATABASE_URL: str | None = Field(
        default=None, description="PostgreSQL database URL for MCP server"
    )
    FIGMA_TOKEN: str | None = Field(default=None, description="Figma API token")

    # Model Configuration
    GEMINI_MODEL: str = Field(default="gemini-3-flash-preview", description="Gemini model name")
    GEMINI_PRO_MODEL: str = Field(default="gemini-2.5-pro", description="Gemini Pro model name")
    OPENAI_MODEL: str = Field(default="gpt-4o", description="OpenAI model name")

    # Thresholds and Limits
    SOVEREIGN_HIGH_CONFIDENCE: float = Field(default=0.75, ge=0.0, le=1.0)
    SOVEREIGN_MEDIUM_CONFIDENCE: float = Field(default=0.50, ge=0.0, le=1.0)
    RAG_SIMILARITY_THRESHOLD: float = Field(default=0.8, ge=0.0, le=1.0)
    GOVERNOR_SAFETY_THRESHOLD: float = Field(default=0.95, ge=0.0, le=1.0)

    # Application Settings
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    DEBUG: bool = Field(default=False, description="Debug mode flag")
    PYTHONUNBUFFERED: str = Field(default="1", description="Python unbuffered output")

    # Hive Mind Configuration
    HIVE_MIND_STRICT_MODE: bool = Field(default=False, description="Strict mode for Hive Mind")
    HIVE_MIND_MIN_CONFIDENCE: float = Field(default=0.98, ge=0.0, le=1.0)
    HIVE_MIND_TRACE_SAMPLING_RATE: float = Field(default=1.0, ge=0.0, le=1.0)
    HIVE_MIND_PROMOTION_THRESHOLD: float = Field(default=0.8, ge=0.0, le=1.0)
    HIVE_MIND_WORKING_MEMORY_TTL: int = Field(default=86400, ge=0)
    HIVE_MIND_LONG_TERM_TTL: int = Field(default=604800, ge=0)


@dataclass
class EnvironmentValidationResult:
    """Result of environment validation."""

    valid: bool
    missing_required: list[str] = field(default_factory=list)
    missing_optional: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    config: EnvironmentConfig | None = None


class EnvironmentValidator:
    """Validates environment variables and provides fail-fast startup checks."""

    REQUIRED_VARS: Final[list[str]] = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
        "PINECONE_API_KEY",
    ]

    OPTIONAL_VARS: Final[list[str]] = [
        "MISTRALAI_API_KEY",
        "COHERE_API_KEY",
        "GROQ_API_KEY",
        "TOGETHER_API_KEY",
        "FIREWORKS_API_KEY",
        "BRAVE_SEARCH_API_KEY",
        "GITHUB_TOKEN",
        "DATABASE_URL",
        "FIGMA_TOKEN",
    ]

    @classmethod
    def validate(cls, raise_on_missing: bool = True) -> EnvironmentValidationResult:
        """
        Validate environment variables.

        Args:
            raise_on_missing: If True, raises EnvironmentError on missing required vars

        Returns:
            EnvironmentValidationResult with validation details

        Raises:
            EnvironmentError: If required variables are missing and raise_on_missing=True
        """
        missing_required = []
        missing_optional = []
        errors = []

        # Check required variables
        for var in cls.REQUIRED_VARS:
            value = os.getenv(var)
            if not value or value.strip() == "":
                missing_required.append(var)

        # Check optional variables
        for var in cls.OPTIONAL_VARS:
            value = os.getenv(var)
            if not value or value.strip() == "":
                missing_optional.append(var)

        # Try to load configuration by explicitly passing env values
        config = None
        try:
            # Build kwargs from environment variables
            env_kwargs = {}
            for field_name in EnvironmentConfig.model_fields:
                value = os.getenv(field_name)
                if value is not None:
                    env_kwargs[field_name] = value
            config = EnvironmentConfig(**env_kwargs)
        except ValidationError as e:
            for error in e.errors():
                field_name = ".".join(str(loc) for loc in error["loc"])
                errors.append(f"{field_name}: {error['msg']}")

        # Determine validity
        valid = len(missing_required) == 0 and len(errors) == 0

        result = EnvironmentValidationResult(
            valid=valid,
            missing_required=missing_required,
            missing_optional=missing_optional,
            errors=errors,
            config=config if valid else None,
        )

        if raise_on_missing and not valid:
            error_msg = cls._format_error_message(result)
            raise OSError(error_msg)

        return result

    @classmethod
    def _format_error_message(cls, result: EnvironmentValidationResult) -> str:
        """Format a detailed error message for validation failures."""
        lines = ["Environment validation failed:"]

        if result.missing_required:
            lines.append("\nMissing required variables:")
            for var in result.missing_required:
                lines.append(f"  - {var}")

        if result.errors:
            lines.append("\nValidation errors:")
            for error in result.errors:
                lines.append(f"  - {error}")

        if result.missing_optional:
            lines.append("\nMissing optional variables (functionality may be limited):")
            for var in result.missing_optional:
                lines.append(f"  - {var}")

        lines.append("\nPlease check your .env file and ensure all required variables are set.")
        return "\n".join(lines)

    @classmethod
    def get_config(cls) -> EnvironmentConfig:
        """
        Get validated environment configuration.

        Returns:
            EnvironmentConfig instance

        Raises:
            EnvironmentError: If validation fails
        """
        result = cls.validate(raise_on_missing=True)
        if result.config is None:
            raise OSError("Failed to load environment configuration")
        return result.config

    @classmethod
    def validate_startup(cls) -> None:
        """
        Perform startup validation with detailed error reporting.

        Raises:
            EnvironmentError: If validation fails
        """
        result = cls.validate(raise_on_missing=False)

        if not result.valid:
            error_msg = cls._format_error_message(result)
            raise OSError(error_msg)

        # Log optional missing variables as warnings
        if result.missing_optional:
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(
                "Optional environment variables not set: %s", ", ".join(result.missing_optional)
            )


# Singleton instance
_config_instance: EnvironmentConfig | None = None


def get_environment_config() -> EnvironmentConfig:
    """
    Get singleton environment configuration instance.

    Returns:
        EnvironmentConfig instance

    Raises:
        EnvironmentError: If validation fails
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = EnvironmentValidator.get_config()
    return _config_instance


def validate_environment() -> None:
    """
    Validate environment at startup.

    Raises:
        EnvironmentError: If validation fails
    """
    EnvironmentValidator.validate_startup()
