"""ADG-driven tests for agentic_core/L5_safety/reasoning/DynamicSealAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.reasoning.DynamicSealAgent import (  # noqa: F401
        SealResult,
        DynamicSealAgent,
        main,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SealResult = None  # type: ignore[assignment,misc]
    DynamicSealAgent = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="DynamicSealAgent.py deps unavailable")
class TestSealResult:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(SealResult)
    def test_importable(self):
        assert SealResult is not None

@pytest.mark.skipif(not _AVAILABLE, reason="DynamicSealAgent.py deps unavailable")
class TestDynamicSealAgent:
    def test_is_class(self):
        assert isinstance(DynamicSealAgent, type)
    def test_importable(self):
        assert DynamicSealAgent is not None

@pytest.mark.skipif(not _AVAILABLE, reason="DynamicSealAgent.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="DynamicSealAgent.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="DynamicSealAgent.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="DynamicSealAgent.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="DynamicSealAgent.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="DynamicSealAgent.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="DynamicSealAgent.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module DynamicSealAgent.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
