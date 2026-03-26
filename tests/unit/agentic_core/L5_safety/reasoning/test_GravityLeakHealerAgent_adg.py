"""ADG importability contract for agentic_core/L5_safety/reasoning/GravityLeakHealerAgent.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.reasoning.GravityLeakHealerAgent as _mod  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.reasoning.GravityLeakHealerAgent as _mod  # noqa: F401
    """Module GravityLeakHealerAgent must be importable."""
    assert _mod is not None
