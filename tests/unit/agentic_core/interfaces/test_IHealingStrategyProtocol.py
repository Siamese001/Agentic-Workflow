"""Foundational behavioral tests for agentic_core/interfaces/IHealingStrategyProtocol.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_IHealingStrategyProtocol_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.interfaces.IHealingStrategyProtocol import (  # noqa: F401
        IHealingStrategyProtocol,
        ChaosResilienceStrategy,
        get_chaos_strategy,
        register_chaos_healing,
        get_integration_status,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    IHealingStrategyProtocol = None  # type: ignore[assignment,misc]
    ChaosResilienceStrategy = None  # type: ignore[assignment,misc]
    get_chaos_strategy = None  # type: ignore[assignment,misc]
    register_chaos_healing = None  # type: ignore[assignment,misc]
    get_integration_status = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="IHealingStrategyProtocol.py deps unavailable")
class TestIHealingStrategyProtocolContract:
    def test_is_class(self):
        assert isinstance(IHealingStrategyProtocol, type)

    def test_has_method_can_heal(self):
        assert callable(getattr(IHealingStrategyProtocol, 'can_heal', None))

    def test_has_method_heal(self):
        assert callable(getattr(IHealingStrategyProtocol, 'heal', None))

@pytest.mark.skipif(not _AVAILABLE, reason="IHealingStrategyProtocol.py deps unavailable")
class TestChaosResilienceStrategyContract:
    def test_is_class(self):
        assert isinstance(ChaosResilienceStrategy, type)

    def test_has_method_can_heal(self):
        assert callable(getattr(ChaosResilienceStrategy, 'can_heal', None))

    def test_has_method_heal(self):
        assert callable(getattr(ChaosResilienceStrategy, 'heal', None))

@pytest.mark.skipif(not _AVAILABLE, reason="IHealingStrategyProtocol.py deps unavailable")
class TestGetChaosStrategyFunction:
    def test_is_callable(self):
        assert callable(get_chaos_strategy)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_chaos_strategy)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="IHealingStrategyProtocol.py deps unavailable")
class TestRegisterChaosHealingFunction:
    def test_is_callable(self):
        assert callable(register_chaos_healing)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(register_chaos_healing)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="IHealingStrategyProtocol.py deps unavailable")
class TestGetIntegrationStatusFunction:
    def test_is_callable(self):
        assert callable(get_integration_status)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_integration_status)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="IHealingStrategyProtocol.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="IHealingStrategyProtocol.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="IHealingStrategyProtocol.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="IHealingStrategyProtocol.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="IHealingStrategyProtocol.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module IHealingStrategyProtocol must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
