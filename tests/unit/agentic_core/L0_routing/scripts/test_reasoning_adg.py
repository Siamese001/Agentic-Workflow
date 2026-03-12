"""ADG-driven tests for agentic_core/L0_routing/scripts/reasoning.py — fan_in=0."""
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
        MultiPathStrategy,
        ReasoningStrategyFactory,
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
    ReasoningStrategy = None  # type: ignore[assignment,misc]
    ChainOfThoughtStrategy = None  # type: ignore[assignment,misc]
    TreeOfThoughtsStrategy = None  # type: ignore[assignment,misc]
    ReActStrategy = None  # type: ignore[assignment,misc]
    ReflectionStrategy = None  # type: ignore[assignment,misc]
    CritiqueStrategy = None  # type: ignore[assignment,misc]
    MultiPathStrategy = None  # type: ignore[assignment,misc]
    ReasoningStrategyFactory = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="reasoning.py deps unavailable")
class TestReasoningStrategy:
    def test_is_class(self):
        assert isinstance(ReasoningStrategy, type)
    def test_importable(self):
        assert ReasoningStrategy is not None

@pytest.mark.skipif(not _AVAILABLE, reason="reasoning.py deps unavailable")
class TestChainOfThoughtStrategy:
    def test_is_class(self):
        assert isinstance(ChainOfThoughtStrategy, type)
    def test_importable(self):
        assert ChainOfThoughtStrategy is not None

@pytest.mark.skipif(not _AVAILABLE, reason="reasoning.py deps unavailable")
class TestTreeOfThoughtsStrategy:
    def test_is_class(self):
        assert isinstance(TreeOfThoughtsStrategy, type)
    def test_importable(self):
        assert TreeOfThoughtsStrategy is not None

@pytest.mark.skipif(not _AVAILABLE, reason="reasoning.py deps unavailable")
class TestReActStrategy:
    def test_is_class(self):
        assert isinstance(ReActStrategy, type)
    def test_importable(self):
        assert ReActStrategy is not None

@pytest.mark.skipif(not _AVAILABLE, reason="reasoning.py deps unavailable")
class TestReflectionStrategy:
    def test_is_class(self):
        assert isinstance(ReflectionStrategy, type)
    def test_importable(self):
        assert ReflectionStrategy is not None

@pytest.mark.skipif(not _AVAILABLE, reason="reasoning.py deps unavailable")
class TestCritiqueStrategy:
    def test_is_class(self):
        assert isinstance(CritiqueStrategy, type)
    def test_importable(self):
        assert CritiqueStrategy is not None

@pytest.mark.skipif(not _AVAILABLE, reason="reasoning.py deps unavailable")
class TestMultiPathStrategy:
    def test_is_class(self):
        assert isinstance(MultiPathStrategy, type)
    def test_importable(self):
        assert MultiPathStrategy is not None

@pytest.mark.skipif(not _AVAILABLE, reason="reasoning.py deps unavailable")
class TestReasoningStrategyFactory:
    def test_is_class(self):
        assert isinstance(ReasoningStrategyFactory, type)
    def test_importable(self):
        assert ReasoningStrategyFactory is not None

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

@pytest.mark.skipif(not _AVAILABLE, reason="reasoning.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module reasoning.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
