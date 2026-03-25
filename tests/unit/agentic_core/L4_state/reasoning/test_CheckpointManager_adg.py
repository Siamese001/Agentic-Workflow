"""ADG importability contract for agentic_core/L4_state/reasoning/CheckpointManager.py."""
from __future__ import annotations

import agentic_core.L4_state.reasoning.CheckpointManager  # noqa: F401


def test_module_importable():
    """Module CheckpointManager must be importable."""
    assert agentic_core.L4_state.reasoning.CheckpointManager is not None
