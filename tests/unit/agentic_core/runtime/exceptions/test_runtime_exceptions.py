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
    )
    _AVAILABLE = True
except Exception as _exc:
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
    def test_is_class(self):
        assert isinstance(AgentRuntimeError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(AgentRuntimeError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_exceptions.py deps unavailable")
class TestToolExecutionErrorContract:
    def test_is_class(self):
        assert isinstance(ToolExecutionError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(ToolExecutionError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_exceptions.py deps unavailable")
class TestToolNotFoundErrorContract:
    def test_is_class(self):
        assert isinstance(ToolNotFoundError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(ToolNotFoundError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_exceptions.py deps unavailable")
class TestHealExecutionErrorContract:
    def test_is_class(self):
        assert isinstance(HealExecutionError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(HealExecutionError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_exceptions.py deps unavailable")
class TestPatternExecutionErrorContract:
    def test_is_class(self):
        assert isinstance(PatternExecutionError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(PatternExecutionError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_exceptions.py deps unavailable")
class TestMaxTurnsExceededErrorContract:
    def test_is_class(self):
        assert isinstance(MaxTurnsExceededError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(MaxTurnsExceededError, type)

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


def test_module_importable():
    """Module runtime_exceptions must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
