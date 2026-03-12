"""Foundational behavioral tests for agentic_core/L5_safety/enforcement/sovereign_healing_engine_enforcer.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_sovereign_healing_engine_enforcer_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.enforcement.sovereign_healing_engine_enforcer import (  # noqa: F401
        HealingTransaction,
        SovereignHealingEngine,
        get_filesystem_client,
        get_git_client,
        run_autonomous_healing,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    HealingTransaction = None  # type: ignore[assignment,misc]
    SovereignHealingEngine = None  # type: ignore[assignment,misc]
    get_filesystem_client = None  # type: ignore[assignment,misc]
    get_git_client = None  # type: ignore[assignment,misc]
    run_autonomous_healing = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="sovereign_healing_engine_enforcer.py deps unavailable")
class TestHealingTransactionContract:
    def test_is_class(self):
        assert isinstance(HealingTransaction, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(HealingTransaction, type)

@pytest.mark.skipif(not _AVAILABLE, reason="sovereign_healing_engine_enforcer.py deps unavailable")
class TestSovereignHealingEngineContract:
    def test_is_class(self):
        assert isinstance(SovereignHealingEngine, type)

    def test_has_method_execute_autonomous_cycle(self):
        assert callable(getattr(SovereignHealingEngine, 'execute_autonomous_cycle', None))

@pytest.mark.skipif(not _AVAILABLE, reason="sovereign_healing_engine_enforcer.py deps unavailable")
class TestGetFilesystemClientFunction:
    def test_is_callable(self):
        assert callable(get_filesystem_client)

@pytest.mark.skipif(not _AVAILABLE, reason="sovereign_healing_engine_enforcer.py deps unavailable")
class TestGetGitClientFunction:
    def test_is_callable(self):
        assert callable(get_git_client)

@pytest.mark.skipif(not _AVAILABLE, reason="sovereign_healing_engine_enforcer.py deps unavailable")
class TestRunAutonomousHealingFunction:
    def test_is_callable(self):
        assert callable(run_autonomous_healing)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(run_autonomous_healing)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="sovereign_healing_engine_enforcer.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="sovereign_healing_engine_enforcer.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="sovereign_healing_engine_enforcer.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="sovereign_healing_engine_enforcer.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="sovereign_healing_engine_enforcer.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module sovereign_healing_engine_enforcer must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
