"""ADG importability contract for agentic_core/L5_safety/reasoning/RedSentinelAgent.py."""
from __future__ import annotations

import agentic_core.L5_safety.reasoning.RedSentinelAgent  # noqa: F401


def test_module_importable():
    """Module RedSentinelAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.RedSentinelAgent is not None
