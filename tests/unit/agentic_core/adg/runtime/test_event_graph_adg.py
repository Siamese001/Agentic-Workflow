"""ADG importability contract for agentic_core/adg/runtime/event_graph.py."""
from __future__ import annotations

import agentic_core.adg.runtime.event_graph  # noqa: F401


def test_module_importable():
    """Module event_graph must be importable."""
    assert agentic_core.adg.runtime.event_graph is not None
