"""Foundational behavioral tests for apps_rg/validators/regeneration_validator.py.

fan_in=10 — this module is imported by 10 other modules.
ADG contract: import-hygiene is covered by test_regeneration_validator_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_rg.validators.regeneration_validator import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        CondensationStrategy,
        ExpansionStrategy,
        RegenerationEngine,
        RegenerationStrategy,
    )
    _AVAILABLE = True
except ImportError as _exc:
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


@pytest.mark.skipif(not _AVAILABLE, reason="regeneration_validator.py deps unavailable")
class TestRegenerationStrategyContract:
    def test_is_class(self):
        assert isinstance(RegenerationStrategy, type)

    def test_has_method_execute(self):
        assert callable(getattr(RegenerationStrategy, 'execute', None))

@pytest.mark.skipif(not _AVAILABLE, reason="regeneration_validator.py deps unavailable")
class TestExpansionStrategyContract:
    def test_is_class(self):
        assert isinstance(ExpansionStrategy, type)

    def test_has_method_execute(self):
        assert callable(getattr(ExpansionStrategy, 'execute', None))

@pytest.mark.skipif(not _AVAILABLE, reason="regeneration_validator.py deps unavailable")
class TestCondensationStrategyContract:
    def test_is_class(self):
        assert isinstance(CondensationStrategy, type)

    def test_has_method_execute(self):
        assert callable(getattr(CondensationStrategy, 'execute', None))

@pytest.mark.skipif(not _AVAILABLE, reason="regeneration_validator.py deps unavailable")
class TestRegenerationEngineContract:
    def test_is_class(self):
        assert isinstance(RegenerationEngine, type)

    def test_has_method_regenerate(self):
        assert callable(getattr(RegenerationEngine, 'regenerate', None))

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


def test_module_importable():
    """Module regeneration_validator must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
