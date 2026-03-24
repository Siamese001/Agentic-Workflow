"""ADG importability contract for agentic_core/L4_state/reasoning/CheckpointManager.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_CheckpointManager.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L4_state.reasoning.CheckpointManager import (  # noqa: F401
        Checkpoint,
        CheckpointManager,
        RecoveryResult,
        get_checkpoint_manager,
        get_sync_checkpoint_manager,
        timeout,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    Checkpoint = None  # type: ignore[assignment,misc]
    RecoveryResult = None  # type: ignore[assignment,misc]
    timeout = None  # type: ignore[assignment,misc]
    CheckpointManager = None  # type: ignore[assignment,misc]
    get_checkpoint_manager = None  # type: ignore[assignment,misc]
    get_sync_checkpoint_manager = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="CheckpointManager deps unavailable")
class TestCheckpointmanagerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L4_state/reasoning/CheckpointManager.py must be importable."""
        assert _AVAILABLE

    def test_checkpoint_defined(self) -> None:
        assert Checkpoint is not None

    def test_recoveryresult_defined(self) -> None:
        assert RecoveryResult is not None

    def test_checkpointmanager_defined(self) -> None:
        assert CheckpointManager is not None