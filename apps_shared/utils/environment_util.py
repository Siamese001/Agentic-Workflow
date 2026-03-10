"""
Environment Variable Validation Utilities.

Provides fail-fast environment validation for all required API keys and configuration.
Phase 3 - Semantic split: validation logic only (schema in environment_config.py).
"""

from __future__ import annotations

import os
from typing import Final

from pydantic import ValidationError

from apps_shared.config.environment_config import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    EnvironmentConfig,
    EnvironmentValidationResult,
)

__all__ = [
    "EnvironmentConfig",
    "EnvironmentValidationResult",
    "EnvironmentValidator",
    "get_environment_config",
    "validate_environment",
]


class EnvironmentValidator:
    """Validates environment variables and provides fail-fast startup checks."""

    REQUIRED_VARS: Final[list[str]] = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
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
                "Optional environment variables not set: %s",
                ", ".join(result.missing_optional),
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
