"""Tests for apps_qwen configuration classes."""

import pytest

from apps_qwen.config.apps_qwen_config import (
    AppsQwenConfig,
    AppsQwenModelConfig,
    AppsQwenPromptConfig,
)


class TestAppsQwenModelConfig:
    """Test AppsQwenModelConfig dataclass."""

    def test_model_config_creation(self):
        """Test creating a model configuration."""
        config = AppsQwenModelConfig(
            model_id="Qwen/Qwen2.5-7B-Instruct",
            max_tokens=1024,
            temperature=0.1,
            confidence_threshold=0.6,
            timeout_seconds=30,
        )
        assert config.model_id == "Qwen/Qwen2.5-7B-Instruct"
        assert config.max_tokens == 1024
        assert config.temperature == 0.1
        assert config.confidence_threshold == 0.6
        assert config.timeout_seconds == 30

    def test_model_config_immutability(self):
        """Test that model config is frozen (immutable)."""
        config = AppsQwenModelConfig(
            model_id="Qwen/Qwen2.5-7B-Instruct",
            max_tokens=1024,
            temperature=0.1,
            confidence_threshold=0.6,
            timeout_seconds=30,
        )
        with pytest.raises(AttributeError):
            config.model_id = "different_model"


class TestAppsQwenPromptConfig:
    """Test AppsQwenPromptConfig dataclass."""

    def test_prompt_config_creation(self):
        """Test creating a prompt configuration."""
        config = AppsQwenPromptConfig(
            app_name="test_app",
            prompt_templates={"default": "Test prompt"},
            default_template="default",
        )
        assert config.app_name == "test_app"
        assert config.prompt_templates == {"default": "Test prompt"}
        assert config.default_template == "default"


class TestAppsQwenConfig:
    """Test AppsQwenConfig central configuration manager."""

    def test_model_configs_exist(self):
        """Test that predefined model configurations exist."""
        assert hasattr(AppsQwenConfig, "MODEL_CONFIGS")
        assert isinstance(AppsQwenConfig.MODEL_CONFIGS, dict)
        assert len(AppsQwenConfig.MODEL_CONFIGS) > 0

    def test_fast_inference_config_exists(self):
        """Test that fast_inference configuration exists."""
        assert "fast_inference" in AppsQwenConfig.MODEL_CONFIGS
        config = AppsQwenConfig.MODEL_CONFIGS["fast_inference"]
        assert isinstance(config, AppsQwenModelConfig)
        assert config.temperature == 0.1

    def test_complex_reasoning_config_exists(self):
        """Test that complex_reasoning configuration exists."""
        assert "complex_reasoning" in AppsQwenConfig.MODEL_CONFIGS
        config = AppsQwenConfig.MODEL_CONFIGS["complex_reasoning"]
        assert isinstance(config, AppsQwenModelConfig)
        assert config.temperature == 0.2  # Complete validation with correct value
