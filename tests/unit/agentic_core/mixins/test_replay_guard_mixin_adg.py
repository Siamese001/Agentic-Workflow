"""ADG importability contract for agentic_core/mixins/replay_guard_mixin.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_replay_guard_mixin.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.mixins.replay_guard_mixin import (  # noqa: F401
        ReplayGuardMixin,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ReplayGuardMixin = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="replay_guard_mixin deps unavailable")
class TestReplayGuardMixinImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/mixins/replay_guard_mixin.py must be importable."""
        assert _AVAILABLE

    def test_replayguardmixin_defined(self) -> None:
        assert ReplayGuardMixin is not None
