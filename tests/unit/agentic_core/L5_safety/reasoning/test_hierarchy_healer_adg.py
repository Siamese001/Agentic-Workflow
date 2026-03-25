"""ADG importability contract for agentic_core/L5_safety/reasoning/hierarchy_healer.py."""
from __future__ import annotations

import agentic_core.L5_safety.reasoning.hierarchy_healer  # noqa: F401


def test_module_importable():
    """Module hierarchy_healer must be importable."""
    assert agentic_core.L5_safety.reasoning.hierarchy_healer is not None
