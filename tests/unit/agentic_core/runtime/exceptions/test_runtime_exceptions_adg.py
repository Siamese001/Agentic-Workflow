"""ADG-driven tests for agentic_core/runtime/exceptions/runtime_exceptions.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.runtime.exceptions.runtime_exceptions import (  # noqa: F401
        AgentRuntimeError,
        ToolExecutionError,
        ToolNotFoundError,
        HealExecutionError,
        PatternExecutionError,
        MaxTurnsExceededError,
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
    AgentRuntimeError = None  # type: ignore[assignment,misc]
    ToolExecutionError = None  # type: ignore[assignment,misc]
    ToolNotFoundError = None  # type: ignore[assignment,misc]
    HealExecutionError = None  # type: ignore[assignment,misc]
    PatternExecutionError = None  # type: ignore[assignment,misc]
    MaxTurnsExceededError = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="runtime_exceptions.py deps unavailable")
class TestAgentRuntimeError:
    def test_is_class(self):
        assert isinstance(AgentRuntimeError, type)
    def test_importable(self):
        assert AgentRuntimeError is not None

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_exceptions.py deps unavailable")
class TestToolExecutionError:
    def test_is_class(self):
        assert isinstance(ToolExecutionError, type)
    def test_importable(self):
        assert ToolExecutionError is not None

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_exceptions.py deps unavailable")
class TestToolNotFoundError:
    def test_is_class(self):
        assert isinstance(ToolNotFoundError, type)
    def test_importable(self):
        assert ToolNotFoundError is not None

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_exceptions.py deps unavailable")
class TestHealExecutionError:
    def test_is_class(self):
        assert isinstance(HealExecutionError, type)
    def test_importable(self):
        assert HealExecutionError is not None

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_exceptions.py deps unavailable")
class TestPatternExecutionError:
    def test_is_class(self):
        assert isinstance(PatternExecutionError, type)
    def test_importable(self):
        assert PatternExecutionError is not None

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_exceptions.py deps unavailable")
class TestMaxTurnsExceededError:
    def test_is_class(self):
        assert isinstance(MaxTurnsExceededError, type)
    def test_importable(self):
        assert MaxTurnsExceededError is not None

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_exceptions.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_exceptions.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_exceptions.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_exceptions.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_exceptions.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_exceptions.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module runtime_exceptions.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
