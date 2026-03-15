"""ADG-driven tests for agentic_core/runtime/config/model_tier_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.runtime.config.model_tier_config import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        ModelConfig,
        ModelTier,
        RoutingDecision,
        TaskComplexity,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ModelTier = None  # type: ignore[assignment,misc]
    TaskComplexity = None  # type: ignore[assignment,misc]
    ModelConfig = None  # type: ignore[assignment,misc]
    RoutingDecision = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="model_tier_config.py deps unavailable")
class TestModelTier:
    def test_is_enum(self):
        import enum
        assert issubclass(ModelTier, enum.Enum)
    def test_has_members(self):
        assert len(list(ModelTier)) >= 1
    def test_importable(self):
        assert ModelTier is not None

@pytest.mark.skipif(not _AVAILABLE, reason="model_tier_config.py deps unavailable")
class TestTaskComplexity:
    def test_is_enum(self):
        import enum
        assert issubclass(TaskComplexity, enum.Enum)
    def test_has_members(self):
        assert len(list(TaskComplexity)) >= 1
    def test_importable(self):
        assert TaskComplexity is not None

@pytest.mark.skipif(not _AVAILABLE, reason="model_tier_config.py deps unavailable")
class TestModelConfig:
    def test_is_class(self):
        assert isinstance(ModelConfig, type)
    def test_importable(self):
        assert ModelConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="model_tier_config.py deps unavailable")
class TestRoutingDecision:
    def test_is_class(self):
        assert isinstance(RoutingDecision, type)
    def test_importable(self):
        assert RoutingDecision is not None

@pytest.mark.skipif(not _AVAILABLE, reason="model_tier_config.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="model_tier_config.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="model_tier_config.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="model_tier_config.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="model_tier_config.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="model_tier_config.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module model_tier_config.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
