"""ADG importability contract for agentic_core/L5_safety/reasoning/ResourceManagerAgent.py."""
from __future__ import annotations

import agentic_core.L5_safety.reasoning.ResourceManagerAgent  # noqa: F401


def test_module_importable():
    """Module ResourceManagerAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.ResourceManagerAgent is not None
