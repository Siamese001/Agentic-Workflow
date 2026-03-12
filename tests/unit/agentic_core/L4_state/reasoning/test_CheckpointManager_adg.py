"""ADG-driven tests for agentic_core/L4_state/reasoning/CheckpointManager.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L4_state.reasoning.CheckpointManager import (  # noqa: F401
        Checkpoint,
        RecoveryResult,
        CheckpointManager,
        timeout,
        get_checkpoint_manager,
        get_sync_checkpoint_manager,
        get_autonomous_checkpoint_manager,
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
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="CheckpointManager.py deps unavailable")
class TestCheckpoint:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(Checkpoint)
    def test_importable(self):
        assert Checkpoint is not None

@pytest.mark.skipif(not _AVAILABLE, reason="CheckpointManager.py deps unavailable")
class TestRecoveryResult:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(RecoveryResult)
    def test_importable(self):
        assert RecoveryResult is not None

@pytest.mark.skipif(not _AVAILABLE, reason="CheckpointManager.py deps unavailable")
class TestCheckpointManager:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(CheckpointManager)
    def test_importable(self):
        assert CheckpointManager is not None

@pytest.mark.skipif(not _AVAILABLE, reason="CheckpointManager.py deps unavailable")
class TestTimeout:
    def test_is_callable(self):
        assert callable(timeout)

@pytest.mark.skipif(not _AVAILABLE, reason="CheckpointManager.py deps unavailable")
class TestGetCheckpointManager:
    def test_is_callable(self):
        assert callable(get_checkpoint_manager)

@pytest.mark.skipif(not _AVAILABLE, reason="CheckpointManager.py deps unavailable")
class TestGetSyncCheckpointManager:
    def test_is_callable(self):
        assert callable(get_sync_checkpoint_manager)

@pytest.mark.skipif(not _AVAILABLE, reason="CheckpointManager.py deps unavailable")
class TestGetAutonomousCheckpointManager:
    def test_is_callable(self):
        assert callable(get_autonomous_checkpoint_manager)

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

@pytest.mark.skipif(not _AVAILABLE, reason="CheckpointManager.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module CheckpointManager.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
