"""ADG importability contract for agentic_core/L5_safety/reasoning/SecurityManagerAgent.py."""
from __future__ import annotations

import agentic_core.L5_safety.reasoning.SecurityManagerAgent  # noqa: F401


def test_module_importable():
    """Module SecurityManagerAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.SecurityManagerAgent is not None
