"""ADG importability contract for agentic_core/L4_state/enforcement/graph_memory_bridge.py."""
from __future__ import annotations

import agentic_core.L4_state.enforcement.graph_memory_bridge  # noqa: F401


def test_module_importable():
    """Module graph_memory_bridge must be importable."""
    assert agentic_core.L4_state.enforcement.graph_memory_bridge is not None
