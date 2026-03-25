"""ADG importability contract for agentic_core/L5_safety/reasoning/SystemArchitectAgent.py."""
from __future__ import annotations

import agentic_core.L5_safety.reasoning.SystemArchitectAgent  # noqa: F401


def test_module_importable():
    """Module SystemArchitectAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.SystemArchitectAgent is not None
