"""ADG importability contract for agentic_core/L5_safety/reasoning/StructureEnforcerAgent.py."""
from __future__ import annotations

import agentic_core.L5_safety.reasoning.StructureEnforcerAgent  # noqa: F401


def test_module_importable():
    """Module StructureEnforcerAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.StructureEnforcerAgent is not None
