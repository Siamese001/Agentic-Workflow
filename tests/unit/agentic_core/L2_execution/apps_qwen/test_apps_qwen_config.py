"""Tests for apps_qwen_config module."""

from __future__ import annotations

import importlib
import unittest
from importlib.util import find_spec
from typing import Any

import pytest

# Check if apps_qwen is available
APPS_QWEN_AVAILABLE = find_spec("agentic_core.L2_execution.apps_qwen.apps_qwen_config") is not None

if APPS_QWEN_AVAILABLE:
    _apps_qwen_config: Any = importlib.import_module("agentic_core.L2_execution.apps_qwen.apps_qwen_config")
else:
    _apps_qwen_config: Any = None


@pytest.mark.skipif(
    not APPS_QWEN_AVAILABLE,
    reason="apps_qwen modules not available",
)
class TestAppsQwenConfig(unittest.TestCase):
    """Test class for AppsQwenConfig."""

    def test_get_model_config(self):
        """Test get_model_config method."""
        config = _apps_qwen_config.AppsQwenConfig()
        result = config.get_model_config("fast_inference")
        self.assertIsNotNone(result)
        self.assertEqual(result.model_id, "Qwen/Qwen2.5-7B-Instruct")

    def test_get_prompt_config(self):
        """Test get_prompt_config method."""
        config = _apps_qwen_config.AppsQwenConfig()
        result = config.get_prompt_config("apps_research")
        self.assertIsNotNone(result)
        self.assertEqual(result.app_name, "apps_research")

    def test_AppsQwenModelConfig_init(self):
        """Test AppsQwenModelConfig initialization."""
        instance = _apps_qwen_config.AppsQwenModelConfig(
            model_id="Qwen/Qwen2.5-7B-Instruct",
            max_tokens=1024,
            temperature=0.3,
            confidence_threshold=0.7,
            timeout_seconds=30,
        )
        self.assertIsNotNone(instance)
        self.assertEqual(instance.model_id, "Qwen/Qwen2.5-7B-Instruct")
        self.assertEqual(instance.max_tokens, 1024)

    def test_AppsQwenPromptConfig_init(self):
        """Test AppsQwenPromptConfig initialization."""
        instance = _apps_qwen_config.AppsQwenPromptConfig(
            app_name="test_app",
            prompt_templates={"default": "test prompt"},
            default_template="default",
        )
        self.assertIsNotNone(instance)
        self.assertEqual(instance.app_name, "test_app")


if __name__ == "__main__":
    unittest.main()
