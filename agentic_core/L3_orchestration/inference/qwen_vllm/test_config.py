"""Tests for Qwen vLLM inference configuration classes."""

import pytest

from agentic_core.L3_orchestration.inference.qwen_vllm.config import (
    QwenInferenceConfig,
    QwenModelConfig,
    QwenPromptConfig,
)


class TestQwenModelConfig:
    """Test QwenModelConfig dataclass."""

    def test_model_config_creation(self):
        """Test creating a model configuration."""
        config = QwenModelConfig(
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
        config = QwenModelConfig(
            model_id="Qwen/Qwen2.5-7B-Instruct",
            max_tokens=1024,
            temperature=0.1,
            confidence_threshold=0.6,
            timeout_seconds=30,
        )
        with pytest.raises(AttributeError):
            config.model_id = "different_model"


class TestQwenPromptConfig:
    """Test QwenPromptConfig dataclass."""

    def test_prompt_config_creation(self):
        """Test creating a prompt configuration."""
        config = QwenPromptConfig(
            app_name="test_app",
            prompt_templates={"default": "Test prompt"},
            default_template="default",
        )
        assert config.app_name == "test_app"
        assert config.prompt_templates == {"default": "Test prompt"}
        assert config.default_template == "default"


class TestQwenInferenceConfig:
    """Test QwenInferenceConfig central configuration manager."""

    def test_model_configs_exist(self):
        """Test that predefined model configurations exist."""
        assert hasattr(QwenInferenceConfig, "MODEL_CONFIGS")
        assert isinstance(QwenInferenceConfig.MODEL_CONFIGS, dict)
        assert len(QwenInferenceConfig.MODEL_CONFIGS) > 0

    def test_fast_inference_config_exists(self):
        """Test that fast_inference configuration exists."""
        assert "fast_inference" in QwenInferenceConfig.MODEL_CONFIGS
        config = QwenInferenceConfig.MODEL_CONFIGS["fast_inference"]
        assert isinstance(config, QwenModelConfig)
        assert config.temperature == 0.1

    def test_complex_reasoning_config_exists(self):
        """Test that complex_reasoning configuration exists."""
        assert "complex_reasoning" in QwenInferenceConfig.MODEL_CONFIGS
        config = QwenInferenceConfig.MODEL_CONFIGS["complex_reasoning"]
        assert isinstance(config, QwenModelConfig)
        assert config.temperature == 0.2  # Complete validation with correct value
