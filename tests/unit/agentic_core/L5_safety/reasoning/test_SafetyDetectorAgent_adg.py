"""ADG importability contract for agentic_core/L5_safety/reasoning/SafetyDetectorAgent.py."""
from __future__ import annotations

import agentic_core.L5_safety.reasoning.SafetyDetectorAgent  # noqa: F401


def test_module_importable():
    """Module SafetyDetectorAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.SafetyDetectorAgent is not None
