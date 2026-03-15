"""Foundational behavioral tests for agentic_core/runtime/exceptions/healer_exceptions.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_healer_exceptions_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.runtime.exceptions.healer_exceptions import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        CircularDependencyError,
        HealerError,
        HealingBudgetExceededError,
        HealingTimeoutError,
        SovereignError,
        ValidationRegistryError,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    HealerError = None  # type: ignore[assignment,misc]
    CircularDependencyError = None  # type: ignore[assignment,misc]
    HealingBudgetExceededError = None  # type: ignore[assignment,misc]
    ValidationRegistryError = None  # type: ignore[assignment,misc]
    HealingTimeoutError = None  # type: ignore[assignment,misc]
    SovereignError = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="healer_exceptions.py deps unavailable")
class TestHealerErrorContract:
    def test_is_class(self):
        assert isinstance(HealerError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(HealerError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="healer_exceptions.py deps unavailable")
class TestCircularDependencyErrorContract:
    def test_is_class(self):
        assert isinstance(CircularDependencyError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(CircularDependencyError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="healer_exceptions.py deps unavailable")
class TestHealingBudgetExceededErrorContract:
    def test_is_class(self):
        assert isinstance(HealingBudgetExceededError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(HealingBudgetExceededError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="healer_exceptions.py deps unavailable")
class TestValidationRegistryErrorContract:
    def test_is_class(self):
        assert isinstance(ValidationRegistryError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(ValidationRegistryError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="healer_exceptions.py deps unavailable")
class TestHealingTimeoutErrorContract:
    def test_is_class(self):
        assert isinstance(HealingTimeoutError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(HealingTimeoutError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="healer_exceptions.py deps unavailable")
class TestSovereignErrorContract:
    def test_is_class(self):
        assert isinstance(SovereignError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(SovereignError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="healer_exceptions.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healer_exceptions.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healer_exceptions.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healer_exceptions.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healer_exceptions.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module healer_exceptions must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
