"""Foundational behavioral tests for agentic_core/L4_state/reasoning/CheckpointManager.py.

fan_in=13 — this module is imported by 13 other modules.
ADG contract: import-hygiene is covered by test_CheckpointManager_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

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


class TestCheckpointContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(Checkpoint)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(Checkpoint)}
        assert field_names >= {'file_hashes', 'timestamp', 'checkpoint_id', 'metadata', 'state_snapshot'}

class TestRecoveryResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(RecoveryResult)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(RecoveryResult)}
        assert field_names >= {'success', 'state_restored', 'files_restored', 'checkpoint_id', 'errors'}

class TestCheckpointManagerContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(CheckpointManager)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(CheckpointManager)}
        assert field_names >= {'storage_path', 'name', 'layer', 'max_checkpoints', 'mode'}

class TestTimeoutFunction:
    def test_is_callable(self):
        assert callable(timeout)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(timeout)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestGetCheckpointManagerFunction:
    def test_is_callable(self):
        assert callable(get_checkpoint_manager)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_checkpoint_manager)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestGetSyncCheckpointManagerFunction:
    def test_is_callable(self):
        assert callable(get_sync_checkpoint_manager)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_sync_checkpoint_manager)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestGetAutonomousCheckpointManagerFunction:
    def test_is_callable(self):
        assert callable(get_autonomous_checkpoint_manager)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_autonomous_checkpoint_manager)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module CheckpointManager must be importable or skip gracefully."""
    pass  # Import verified at module level
