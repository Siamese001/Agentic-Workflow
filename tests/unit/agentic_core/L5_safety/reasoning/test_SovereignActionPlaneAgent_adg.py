"""ADG importability contract for agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py."""
from __future__ import annotations

import agentic_core.L5_safety.reasoning.SovereignActionPlaneAgent  # noqa: F401


def test_module_importable():
    """Module SovereignActionPlaneAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.SovereignActionPlaneAgent is not None
