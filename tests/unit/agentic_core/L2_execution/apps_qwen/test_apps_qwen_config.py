from __future__ import annotations

import pytest

from agentic_core.L2_execution.apps_qwen.apps_qwen_config import AppsQwenConfig


def test_apps_qwen_config_validates() -> None:
    assert AppsQwenConfig.validate_configuration() is True


def test_apps_qwen_config_get_model_known() -> None:
    cfg = AppsQwenConfig.get_model_config("evaluation")

    assert cfg.model_id == "Qwen/Qwen2.5-7B-Instruct"
    assert cfg.max_tokens == 1536
    assert cfg.confidence_threshold == 0.8


def test_apps_qwen_config_unknown_use_case_raises() -> None:
    with pytest.raises(ValueError, match="Unknown use case"):
        AppsQwenConfig.get_model_config("unknown_case")


def test_apps_qwen_config_unknown_app_raises() -> None:
    with pytest.raises(ValueError, match="Unknown app"):
        AppsQwenConfig.get_prompt_config("apps_unknown")
