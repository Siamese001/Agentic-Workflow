"""ADG importability contract for agentic_core/L5_safety/reasoning/ResourceManagerAgent.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.reasoning.ResourceManagerAgent  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.reasoning.ResourceManagerAgent  # noqa: F401
    """Module ResourceManagerAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.ResourceManagerAgent is not None
