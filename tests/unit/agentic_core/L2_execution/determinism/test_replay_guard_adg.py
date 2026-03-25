"""ADG importability contract for agentic_core/L2_execution/determinism/replay_guard.py."""
from __future__ import annotations

import agentic_core.L2_execution.determinism.replay_guard  # noqa: F401


def test_module_importable():
    """Module replay_guard must be importable."""
    assert agentic_core.L2_execution.determinism.replay_guard is not None
