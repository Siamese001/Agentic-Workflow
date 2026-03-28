"""Tests for apps_qwen_config module."""
import unittest

from agentic_core.L2_execution.apps_qwen import (
    AppsQwenConfig,
    AppsQwenModelConfig,
    AppsQwenPromptConfig,
)


class TestAppsQwenConfig(unittest.TestCase):
    """Test class for AppsQwenConfig."""

    def test_get_model_config(self):
        """Test get_model_config method."""
        config = AppsQwenConfig()
        result = config.get_model_config("fast_inference")
        self.assertIsNotNone(result)
        self.assertEqual(result.model_id, "Qwen/Qwen2.5-7B-Instruct")

    def test_get_prompt_config(self):
        """Test get_prompt_config method."""
        config = AppsQwenConfig()
        result = config.get_prompt_config("apps_research")
        self.assertIsNotNone(result)
        self.assertEqual(result.app_name, "apps_research")

    def test_AppsQwenModelConfig_init(self):
        """Test AppsQwenModelConfig initialization."""
        instance = AppsQwenModelConfig(
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
        instance = AppsQwenPromptConfig(
            app_name="test_app",
            prompt_templates={"default": "test prompt"},
            default_template="default",
        )
        self.assertIsNotNone(instance)
        self.assertEqual(instance.app_name, "test_app")


if __name__ == "__main__":
    unittest.main()