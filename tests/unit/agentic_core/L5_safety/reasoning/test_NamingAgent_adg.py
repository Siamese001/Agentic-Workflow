"""ADG importability contract for agentic_core/L5_safety/reasoning/NamingAgent.py."""
from __future__ import annotations

import agentic_core.L5_safety.reasoning.NamingAgent  # noqa: F401


def test_module_importable():
    """Module NamingAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.NamingAgent is not None
