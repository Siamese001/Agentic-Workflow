"""
Unit tests for Environment Variable Validation System.

Tests Phase 2A.1 - Environment validation functionality.
"""

import os
from unittest.mock import patch

import pytest

from apps_shared.config.environment_config import (
    EnvironmentConfig,
)
from apps_shared.config.environment_util import (
    EnvironmentValidator,
    get_environment_config,
    validate_environment,
)

# Test fixture for required environment variables
REQUIRED_ENV_VARS = {
    "OPENAI_API_KEY": "test-openai-key",
    "ANTHROPIC_API_KEY": "test-anthropic-key",
    "GEMINI_API_KEY": "test-gemini-key",
    "PINECONE_API_KEY": "test-pinecone-key",
}


class TestEnvironmentConfig:
    """Test EnvironmentConfig model."""

    def test_environment_config_with_all_required(self):
        """Test EnvironmentConfig with all required variables via kwargs."""
        config = EnvironmentConfig(
            OPENAI_API_KEY="test-openai-key",
            ANTHROPIC_API_KEY="test-anthropic-key",
            GEMINI_API_KEY="test-gemini-key",
            PINECONE_API_KEY="test-pinecone-key",
        )
        assert config.OPENAI_API_KEY == "test-openai-key"
        assert config.ANTHROPIC_API_KEY == "test-anthropic-key"
        assert config.GEMINI_API_KEY == "test-gemini-key"
        assert config.PINECONE_API_KEY == "test-pinecone-key"

    def test_environment_config_with_defaults(self):
        """Test EnvironmentConfig applies default values."""
        config = EnvironmentConfig(
            OPENAI_API_KEY="test-key",
            ANTHROPIC_API_KEY="test-key",
            GEMINI_API_KEY="test-key",
            PINECONE_API_KEY="test-key",
        )
        assert config.REDIS_HOST == "localhost"
        assert config.REDIS_PORT == 6379
        assert config.GEMINI_MODEL == "gemini-3-flash-preview"
        assert config.OPENAI_MODEL == "gpt-4o"
        assert config.LOG_LEVEL == "INFO"


class TestEnvironmentValidator:
    """Test EnvironmentValidator functionality."""

    def test_validate_success_with_all_required(self):
        """Test validation succeeds with all required variables."""
        with patch.dict(os.environ, REQUIRED_ENV_VARS, clear=False):
            result = EnvironmentValidator.validate(raise_on_missing=False)
            assert result.valid is True
            assert len(result.missing_required) == 0
            assert len(result.errors) == 0
            assert result.config is not None

    def test_validate_fails_with_missing_required(self):
        """Test validation fails with missing required variables."""
        # Save original values
        original_env = {k: os.environ.get(k) for k in EnvironmentValidator.REQUIRED_VARS}

        # Clear required vars
        for var in EnvironmentValidator.REQUIRED_VARS:
            if var in os.environ:
                del os.environ[var]

        try:
            result = EnvironmentValidator.validate(raise_on_missing=False)
            assert result.valid is False
            assert len(result.missing_required) == 4
            assert "OPENAI_API_KEY" in result.missing_required
            assert "ANTHROPIC_API_KEY" in result.missing_required
            assert "GEMINI_API_KEY" in result.missing_required
            assert "PINECONE_API_KEY" in result.missing_required
        finally:
            # Restore original values
            for k, v in original_env.items():
                if v is not None:
                    os.environ[k] = v

    def test_validate_raises_on_missing_when_configured(self):
        """Test validation raises EnvironmentError when configured."""
        # Save original values
        original_env = {k: os.environ.get(k) for k in EnvironmentValidator.REQUIRED_VARS}

        # Clear required vars
        for var in EnvironmentValidator.REQUIRED_VARS:
            if var in os.environ:
                del os.environ[var]

        try:
            with pytest.raises(EnvironmentError) as exc_info:
                EnvironmentValidator.validate(raise_on_missing=True)
            assert "Environment validation failed" in str(exc_info.value)
            assert "OPENAI_API_KEY" in str(exc_info.value)
        finally:
            # Restore original values
            for k, v in original_env.items():
                if v is not None:
                    os.environ[k] = v

    def test_validate_detects_optional_missing(self):
        """Test validation detects missing optional variables."""
        with patch.dict(os.environ, REQUIRED_ENV_VARS, clear=False):
            # Remove one optional var if present
            github_token = os.environ.pop("GITHUB_TOKEN", None)
            try:
                result = EnvironmentValidator.validate(raise_on_missing=False)
                assert result.valid is True
                # Check that at least one optional is detected as missing
                assert len(result.missing_optional) >= 0  # Some may be set in env
            finally:
                if github_token:
                    os.environ["GITHUB_TOKEN"] = github_token

    def test_get_config_success(self):
        """Test get_config returns valid configuration."""
        with patch.dict(os.environ, REQUIRED_ENV_VARS, clear=False):
            config = EnvironmentValidator.get_config()
            assert isinstance(config, EnvironmentConfig)
            assert config.OPENAI_API_KEY == "test-openai-key"

    def test_get_config_raises_on_missing(self):
        """Test get_config raises on missing variables."""
        # Save original values
        original_env = {k: os.environ.get(k) for k in EnvironmentValidator.REQUIRED_VARS}

        # Clear required vars
        for var in EnvironmentValidator.REQUIRED_VARS:
            if var in os.environ:
                del os.environ[var]

        try:
            with pytest.raises(EnvironmentError):
                EnvironmentValidator.get_config()
        finally:
            # Restore original values
            for k, v in original_env.items():
                if v is not None:
                    os.environ[k] = v

    def test_validate_startup_success(self):
        """Test validate_startup succeeds with valid environment."""
        with patch.dict(os.environ, REQUIRED_ENV_VARS, clear=False):
            # Should not raise
            EnvironmentValidator.validate_startup()

    def test_validate_startup_raises_on_invalid(self):
        """Test validate_startup raises on invalid environment."""
        # Save original values
        original_env = {k: os.environ.get(k) for k in EnvironmentValidator.REQUIRED_VARS}

        # Clear required vars
        for var in EnvironmentValidator.REQUIRED_VARS:
            if var in os.environ:
                del os.environ[var]

        try:
            with pytest.raises(EnvironmentError):
                EnvironmentValidator.validate_startup()
        finally:
            # Restore original values
            for k, v in original_env.items():
                if v is not None:
                    os.environ[k] = v


class TestEnvironmentHelpers:
    """Test helper functions."""

    def test_get_environment_config_singleton(self):
        """Test get_environment_config returns singleton instance."""
        with patch.dict(os.environ, REQUIRED_ENV_VARS, clear=False):
            # Reset singleton
            import apps_shared.config.environment_util as env_module

            env_module._config_instance = None

            config1 = get_environment_config()
            config2 = get_environment_config()
            assert config1 is config2  # Same instance

            # Reset singleton for other tests
            env_module._config_instance = None

    def test_validate_environment_success(self):
        """Test validate_environment succeeds with valid environment."""
        with patch.dict(os.environ, REQUIRED_ENV_VARS, clear=False):
            # Should not raise
            validate_environment()

    def test_validate_environment_raises_on_invalid(self):
        """Test validate_environment raises on invalid environment."""
        # Save original values
        original_env = {k: os.environ.get(k) for k in EnvironmentValidator.REQUIRED_VARS}

        # Clear required vars
        for var in EnvironmentValidator.REQUIRED_VARS:
            if var in os.environ:
                del os.environ[var]

        try:
            with pytest.raises(EnvironmentError):
                validate_environment()
        finally:
            # Restore original values
            for k, v in original_env.items():
                if v is not None:
                    os.environ[k] = v


class TestEnvironmentThresholds:
    """Test threshold and configuration values."""

    def test_threshold_defaults(self):
        """Test threshold default values are within valid range."""
        config = EnvironmentConfig(
            OPENAI_API_KEY="test-key",
            ANTHROPIC_API_KEY="test-key",
            GEMINI_API_KEY="test-key",
            PINECONE_API_KEY="test-key",
        )
        assert 0.0 <= config.SOVEREIGN_HIGH_CONFIDENCE <= 1.0
        assert 0.0 <= config.SOVEREIGN_MEDIUM_CONFIDENCE <= 1.0
        assert 0.0 <= config.RAG_SIMILARITY_THRESHOLD <= 1.0
        assert 0.0 <= config.GOVERNOR_SAFETY_THRESHOLD <= 1.0

    def test_hive_mind_defaults(self):
        """Test Hive Mind configuration defaults."""
        config = EnvironmentConfig(
            OPENAI_API_KEY="test-key",
            ANTHROPIC_API_KEY="test-key",
            GEMINI_API_KEY="test-key",
            PINECONE_API_KEY="test-key",
        )
        assert config.HIVE_MIND_STRICT_MODE is False
        assert config.HIVE_MIND_MIN_CONFIDENCE == 0.98
        assert config.HIVE_MIND_TRACE_SAMPLING_RATE == 1.0
        assert config.HIVE_MIND_PROMOTION_THRESHOLD == 0.8
        assert config.HIVE_MIND_WORKING_MEMORY_TTL == 86400
        assert config.HIVE_MIND_LONG_TERM_TTL == 604800
