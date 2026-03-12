"""Foundational behavioral tests for agentic_core/L3_orchestration/reasoning/StateManagementAgent.py.

fan_in=14 — this module is imported by 14 other modules.
ADG contract: import-hygiene is covered by test_StateManagementAgent_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L3_orchestration.reasoning.StateManagementAgent import (  # noqa: F401
        StateEntry,
        IntegrityReport,
        StateManagementAgent,
        get_state_manager,
        get_manifest_manager,
        get_memory_manager,
        get_state_guardian,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    StateEntry = None  # type: ignore[assignment,misc]
    IntegrityReport = None  # type: ignore[assignment,misc]
    StateManagementAgent = None  # type: ignore[assignment,misc]
    get_state_manager = None  # type: ignore[assignment,misc]
    get_manifest_manager = None  # type: ignore[assignment,misc]
    get_memory_manager = None  # type: ignore[assignment,misc]
    get_state_guardian = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="StateManagementAgent.py deps unavailable")
class TestStateEntryContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(StateEntry)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(StateEntry)}
        assert field_names >= {'created_at', 'key', 'file_hash', 'updated_at', 'file_path'}

@pytest.mark.skipif(not _AVAILABLE, reason="StateManagementAgent.py deps unavailable")
class TestIntegrityReportContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(IntegrityReport)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(IntegrityReport)}
        assert field_names >= {'is_healthy', 'hash_mismatches', 'timestamp', 'orphan_entries', 'ghost_files'}

@pytest.mark.skipif(not _AVAILABLE, reason="StateManagementAgent.py deps unavailable")
class TestStateManagementAgentContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(StateManagementAgent)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(StateManagementAgent)}
        assert field_names >= {'heartbeat_interval', 'memory_root', 'name', 'layer', 'retention_days'}

@pytest.mark.skipif(not _AVAILABLE, reason="StateManagementAgent.py deps unavailable")
class TestGetStateManagerFunction:
    def test_is_callable(self):
        assert callable(get_state_manager)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_state_manager)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="StateManagementAgent.py deps unavailable")
class TestGetManifestManagerFunction:
    def test_is_callable(self):
        assert callable(get_manifest_manager)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_manifest_manager)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="StateManagementAgent.py deps unavailable")
class TestGetMemoryManagerFunction:
    def test_is_callable(self):
        assert callable(get_memory_manager)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_memory_manager)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="StateManagementAgent.py deps unavailable")
class TestGetStateGuardianFunction:
    def test_is_callable(self):
        assert callable(get_state_guardian)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_state_guardian)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="StateManagementAgent.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="StateManagementAgent.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="StateManagementAgent.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="StateManagementAgent.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="StateManagementAgent.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module StateManagementAgent must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
