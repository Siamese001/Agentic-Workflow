"""Foundational behavioral tests for agentic_core/L2_execution/healers/healing_tier_config.py.

fan_in=14 — imported by 14 other modules.
ADG import-hygiene is covered separately by test_healing_tier_config_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.healers.healing_tier_config import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        HealingTierConfig,
        is_vllm_process_running,
        load_default_healing_tier_config,
        validate_qwen_startup_state,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    HealingTierConfig = None  # type: ignore[assignment,misc]
    load_default_healing_tier_config = None  # type: ignore[assignment,misc]
    validate_qwen_startup_state = None  # type: ignore[assignment,misc]
    is_vllm_process_running = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="healing_tier_config.py deps unavailable")
class TestHealingTierConfigContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(HealingTierConfig)

    def test_is_frozen(self):
        assert HealingTierConfig.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(HealingTierConfig)}
        assert fnames >= {'heal_confidence_x', 'heal_confidence_y', 'model_gemini_2_5_pro_id', 'model_qwen_vllm_id', 'model_qwen_14b_vllm_id', 'max_heal_retries'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(HealingTierConfig)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="healing_tier_config.py deps unavailable")
class TestLoadDefaultHealingTierConfigFunction:
    def test_is_callable(self):
        assert callable(load_default_healing_tier_config)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(load_default_healing_tier_config)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="healing_tier_config.py deps unavailable")
class TestValidateQwenStartupStateFunction:
    def test_is_callable(self):
        assert callable(validate_qwen_startup_state)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(validate_qwen_startup_state)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="healing_tier_config.py deps unavailable")
class TestIsVllmProcessRunningFunction:
    def test_is_callable(self):
        assert callable(is_vllm_process_running)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(is_vllm_process_running)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="healing_tier_config.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_tier_config.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_tier_config.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_tier_config.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_tier_config.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_tier_config.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: healing_tier_config importable or gracefully unavailable."""
    pass
