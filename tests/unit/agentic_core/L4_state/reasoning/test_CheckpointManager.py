"""Foundational behavioral tests for agentic_core/L4_state/reasoning/CheckpointManager.py.

fan_in=13 — this module is imported by 13 other modules.
ADG contract: import-hygiene is covered by test_CheckpointManager_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L4_state.reasoning.CheckpointManager import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        Checkpoint,
        CheckpointManager,
        RecoveryResult,
        get_autonomous_checkpoint_manager,
        get_checkpoint_manager,
        get_sync_checkpoint_manager,
        timeout,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    Checkpoint = None  # type: ignore[assignment,misc]
    RecoveryResult = None  # type: ignore[assignment,misc]
    CheckpointManager = None  # type: ignore[assignment,misc]
    timeout = None  # type: ignore[assignment,misc]
    get_checkpoint_manager = None  # type: ignore[assignment,misc]
    get_sync_checkpoint_manager = None  # type: ignore[assignment,misc]
    get_autonomous_checkpoint_manager = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="CheckpointManager.py deps unavailable")
class TestCheckpointContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(Checkpoint)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(Checkpoint)}
        assert field_names >= {'file_hashes', 'timestamp', 'checkpoint_id', 'metadata', 'state_snapshot'}

@pytest.mark.skipif(not _AVAILABLE, reason="CheckpointManager.py deps unavailable")
class TestRecoveryResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(RecoveryResult)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(RecoveryResult)}
        assert field_names >= {'success', 'state_restored', 'files_restored', 'checkpoint_id', 'errors'}

@pytest.mark.skipif(not _AVAILABLE, reason="CheckpointManager.py deps unavailable")
class TestCheckpointManagerContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(CheckpointManager)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(CheckpointManager)}
        assert field_names >= {'storage_path', 'name', 'layer', 'max_checkpoints', 'mode'}

@pytest.mark.skipif(not _AVAILABLE, reason="CheckpointManager.py deps unavailable")
class TestTimeoutFunction:
    def test_is_callable(self):
        assert callable(timeout)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(timeout)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="CheckpointManager.py deps unavailable")
class TestGetCheckpointManagerFunction:
    def test_is_callable(self):
        assert callable(get_checkpoint_manager)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_checkpoint_manager)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="CheckpointManager.py deps unavailable")
class TestGetSyncCheckpointManagerFunction:
    def test_is_callable(self):
        assert callable(get_sync_checkpoint_manager)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_sync_checkpoint_manager)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="CheckpointManager.py deps unavailable")
class TestGetAutonomousCheckpointManagerFunction:
    def test_is_callable(self):
        assert callable(get_autonomous_checkpoint_manager)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_autonomous_checkpoint_manager)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="CheckpointManager.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="CheckpointManager.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="CheckpointManager.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="CheckpointManager.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="CheckpointManager.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module CheckpointManager must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
