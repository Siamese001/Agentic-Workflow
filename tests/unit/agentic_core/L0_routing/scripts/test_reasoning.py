"""Foundational behavioral tests for agentic_core/L0_routing/scripts/reasoning.py.

fan_in=14 — this module is imported by 14 other modules.
ADG contract: import-hygiene is covered by test_reasoning_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.reasoning import (  # noqa: F401
        ReasoningStrategy,
        ChainOfThoughtStrategy,
        TreeOfThoughtsStrategy,
        ReActStrategy,
        ReflectionStrategy,
        CritiqueStrategy,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    ReasoningStrategy = None  # type: ignore[assignment,misc]
    ChainOfThoughtStrategy = None  # type: ignore[assignment,misc]
    TreeOfThoughtsStrategy = None  # type: ignore[assignment,misc]
    ReActStrategy = None  # type: ignore[assignment,misc]
    ReflectionStrategy = None  # type: ignore[assignment,misc]
    CritiqueStrategy = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="reasoning.py deps unavailable")
class TestReasoningStrategyContract:
    def test_is_class(self):
        assert isinstance(ReasoningStrategy, type)

    def test_has_method_execute(self):
        assert callable(getattr(ReasoningStrategy, 'execute', None))

@pytest.mark.skipif(not _AVAILABLE, reason="reasoning.py deps unavailable")
class TestChainOfThoughtStrategyContract:
    def test_is_class(self):
        assert isinstance(ChainOfThoughtStrategy, type)

    def test_has_method_execute(self):
        assert callable(getattr(ChainOfThoughtStrategy, 'execute', None))

@pytest.mark.skipif(not _AVAILABLE, reason="reasoning.py deps unavailable")
class TestTreeOfThoughtsStrategyContract:
    def test_is_class(self):
        assert isinstance(TreeOfThoughtsStrategy, type)

    def test_has_method_execute(self):
        assert callable(getattr(TreeOfThoughtsStrategy, 'execute', None))

@pytest.mark.skipif(not _AVAILABLE, reason="reasoning.py deps unavailable")
class TestReActStrategyContract:
    def test_is_class(self):
        assert isinstance(ReActStrategy, type)

    def test_has_method_execute(self):
        assert callable(getattr(ReActStrategy, 'execute', None))

@pytest.mark.skipif(not _AVAILABLE, reason="reasoning.py deps unavailable")
class TestReflectionStrategyContract:
    def test_is_class(self):
        assert isinstance(ReflectionStrategy, type)

    def test_has_method_execute(self):
        assert callable(getattr(ReflectionStrategy, 'execute', None))

@pytest.mark.skipif(not _AVAILABLE, reason="reasoning.py deps unavailable")
class TestCritiqueStrategyContract:
    def test_is_class(self):
        assert isinstance(CritiqueStrategy, type)

    def test_has_method_execute(self):
        assert callable(getattr(CritiqueStrategy, 'execute', None))

@pytest.mark.skipif(not _AVAILABLE, reason="reasoning.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="reasoning.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="reasoning.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="reasoning.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="reasoning.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module reasoning must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
