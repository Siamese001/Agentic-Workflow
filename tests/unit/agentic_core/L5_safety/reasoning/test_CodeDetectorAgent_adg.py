"""ADG importability contract for agentic_core/L5_safety/reasoning/CodeDetectorAgent.py."""
from __future__ import annotations

import agentic_core.L5_safety.reasoning.CodeDetectorAgent  # noqa: F401


def test_module_importable():
    """Module CodeDetectorAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.CodeDetectorAgent is not None
