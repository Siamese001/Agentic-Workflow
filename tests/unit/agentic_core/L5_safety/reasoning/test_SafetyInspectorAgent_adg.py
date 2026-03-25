"""ADG importability contract for agentic_core/L5_safety/reasoning/SafetyInspectorAgent.py."""
from __future__ import annotations

import agentic_core.L5_safety.reasoning.SafetyInspectorAgent  # noqa: F401


def test_module_importable():
    """Module SafetyInspectorAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.SafetyInspectorAgent is not None
