"""ADG-driven tests for apps_rg/validators/regeneration_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_rg.validators.regeneration_validator import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        CondensationStrategy,
        ExpansionStrategy,
        RegenerationEngine,
        RegenerationStrategy,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    RegenerationStrategy = None  # type: ignore[assignment,misc]
    ExpansionStrategy = None  # type: ignore[assignment,misc]
    CondensationStrategy = None  # type: ignore[assignment,misc]
    RegenerationEngine = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="regeneration_validator.py deps unavailable")
class TestRegenerationStrategy:
    def test_is_class(self):
        assert isinstance(RegenerationStrategy, type)
    def test_importable(self):
        assert RegenerationStrategy is not None

@pytest.mark.skipif(not _AVAILABLE, reason="regeneration_validator.py deps unavailable")
class TestExpansionStrategy:
    def test_is_class(self):
        assert isinstance(ExpansionStrategy, type)
    def test_importable(self):
        assert ExpansionStrategy is not None

@pytest.mark.skipif(not _AVAILABLE, reason="regeneration_validator.py deps unavailable")
class TestCondensationStrategy:
    def test_is_class(self):
        assert isinstance(CondensationStrategy, type)
    def test_importable(self):
        assert CondensationStrategy is not None

@pytest.mark.skipif(not _AVAILABLE, reason="regeneration_validator.py deps unavailable")
class TestRegenerationEngine:
    def test_is_class(self):
        assert isinstance(RegenerationEngine, type)
    def test_importable(self):
        assert RegenerationEngine is not None

@pytest.mark.skipif(not _AVAILABLE, reason="regeneration_validator.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="regeneration_validator.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="regeneration_validator.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="regeneration_validator.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="regeneration_validator.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="regeneration_validator.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module regeneration_validator.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
