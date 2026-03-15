"""Foundational behavioral tests for agentic_core/runtime/exceptions/runtime_exceptions.py.

fan_in=12 — this module is imported by 12 other modules.
ADG contract: import-hygiene is covered by test_runtime_exceptions_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.runtime.exceptions.runtime_exceptions import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        AgentRuntimeError,
        HealExecutionError,
        MaxTurnsExceededError,
        PatternExecutionError,
        ToolExecutionError,
        ToolNotFoundError,
    )
    _AVAILABLE = True
except ImportError as _exc:
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


@pytest.mark.skipif(not _AVAILABLE, reason="runtime_exceptions.py deps unavailable")
class TestAgentRuntimeErrorContract:
    def test_is_exception_subclass(self):
        assert issubclass(AgentRuntimeError, Exception)

    def test_raises_and_catchable(self):
        with pytest.raises(AgentRuntimeError):
            raise AgentRuntimeError("agent runtime failure")

    def test_message_preserved(self):
        exc = AgentRuntimeError("agent runtime failure")
        assert str(exc) == "agent runtime failure"

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_exceptions.py deps unavailable")
class TestToolExecutionErrorContract:
    def test_is_exception_subclass(self):
        assert issubclass(ToolExecutionError, Exception)

    def test_raises_and_catchable(self):
        with pytest.raises(ToolExecutionError):
            raise ToolExecutionError("tool exec failed")

    def test_message_preserved(self):
        exc = ToolExecutionError("tool exec failed")
        assert str(exc) == "tool exec failed"

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_exceptions.py deps unavailable")
class TestToolNotFoundErrorContract:
    def test_is_exception_subclass(self):
        assert issubclass(ToolNotFoundError, Exception)

    def test_raises_and_catchable(self):
        with pytest.raises(ToolNotFoundError):
            raise ToolNotFoundError("tool not found")

    def test_message_preserved(self):
        exc = ToolNotFoundError("tool not found")
        assert str(exc) == "tool not found"

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_exceptions.py deps unavailable")
class TestHealExecutionErrorContract:
    def test_is_exception_subclass(self):
        assert issubclass(HealExecutionError, Exception)

    def test_raises_and_catchable(self):
        with pytest.raises(HealExecutionError):
            raise HealExecutionError("heal exec failed")

    def test_message_preserved(self):
        exc = HealExecutionError("heal exec failed")
        assert str(exc) == "heal exec failed"

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_exceptions.py deps unavailable")
class TestPatternExecutionErrorContract:
    def test_is_exception_subclass(self):
        assert issubclass(PatternExecutionError, Exception)

    def test_raises_and_catchable(self):
        with pytest.raises(PatternExecutionError):
            raise PatternExecutionError("pattern exec failed")

    def test_message_preserved(self):
        exc = PatternExecutionError("pattern exec failed")
        assert str(exc) == "pattern exec failed"

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_exceptions.py deps unavailable")
class TestMaxTurnsExceededErrorContract:
    def test_is_exception_subclass(self):
        assert issubclass(MaxTurnsExceededError, Exception)

    def test_raises_and_catchable(self):
        with pytest.raises(MaxTurnsExceededError):
            raise MaxTurnsExceededError("max turns exceeded")

    def test_message_preserved(self):
        exc = MaxTurnsExceededError("max turns exceeded")
        assert str(exc) == "max turns exceeded"

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_exceptions.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_positive_int(self):
        assert isinstance(MAX_RETRIES, int)
        assert MAX_RETRIES > 0

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_exceptions.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_positive_number(self):
        assert isinstance(DEFAULT_SLEEP, (int, float))
        assert DEFAULT_SLEEP > 0

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_exceptions.py deps unavailable")
class TestThresholdConstant:
    def test_is_fraction(self):
        assert isinstance(THRESHOLD, (int, float))
        assert 0 < THRESHOLD <= 1.0

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_exceptions.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_positive_int(self):
        assert isinstance(BUFFER_SIZE, int)
        assert BUFFER_SIZE > 0

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_exceptions.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_positive_int(self):
        assert isinstance(BATCH_SIZE, int)
        assert BATCH_SIZE > 0


def test_module_importable():
    """Module runtime_exceptions must be importable or skip gracefully."""
    if not _AVAILABLE:
        pytest.skip("runtime_exceptions.py deps unavailable — import failed")
    assert issubclass(AgentRuntimeError, Exception)
    assert issubclass(ToolExecutionError, Exception)
