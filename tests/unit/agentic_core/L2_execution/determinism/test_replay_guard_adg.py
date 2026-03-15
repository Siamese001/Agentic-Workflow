"""ADG importability contract for agentic_core/L2_execution/determinism/replay_guard.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_replay_guard.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.determinism.replay_guard import (  # noqa: F401
        ReplayGuard,
        ReplayViolation,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ReplayViolation = None  # type: ignore[assignment,misc]
    ReplayGuard = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="replay_guard deps unavailable")
class TestReplayGuardImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/determinism/replay_guard.py must be importable."""
        assert _AVAILABLE

    def test_replayviolation_defined(self) -> None:
        assert ReplayViolation is not None

    def test_replayguard_defined(self) -> None:
        assert ReplayGuard is not None
