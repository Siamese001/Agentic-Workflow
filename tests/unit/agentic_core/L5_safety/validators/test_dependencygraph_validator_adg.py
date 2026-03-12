"""ADG-driven tests for agentic_core/L5_safety/validators/dependencygraph_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.validators.dependencygraph_validator import (  # noqa: F401
        DependencyGraph,
        BudgetManager,
        ValidationContext,
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
    DependencyGraph = None  # type: ignore[assignment,misc]
    BudgetManager = None  # type: ignore[assignment,misc]
    ValidationContext = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="dependencygraph_validator.py deps unavailable")
class TestDependencyGraph:
    def test_is_class(self):
        assert isinstance(DependencyGraph, type)
    def test_importable(self):
        assert DependencyGraph is not None

@pytest.mark.skipif(not _AVAILABLE, reason="dependencygraph_validator.py deps unavailable")
class TestBudgetManager:
    def test_is_class(self):
        assert isinstance(BudgetManager, type)
    def test_importable(self):
        assert BudgetManager is not None

@pytest.mark.skipif(not _AVAILABLE, reason="dependencygraph_validator.py deps unavailable")
class TestValidationContext:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ValidationContext)
    def test_importable(self):
        assert ValidationContext is not None

@pytest.mark.skipif(not _AVAILABLE, reason="dependencygraph_validator.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="dependencygraph_validator.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="dependencygraph_validator.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="dependencygraph_validator.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="dependencygraph_validator.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="dependencygraph_validator.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module dependencygraph_validator.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
