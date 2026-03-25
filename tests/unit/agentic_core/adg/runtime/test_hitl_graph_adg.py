"""ADG importability contract for agentic_core/adg/runtime/hitl_graph.py."""
from __future__ import annotations

import agentic_core.adg.runtime.hitl_graph  # noqa: F401


def test_module_importable():
    """Module hitl_graph must be importable."""
    assert agentic_core.adg.runtime.hitl_graph is not None
