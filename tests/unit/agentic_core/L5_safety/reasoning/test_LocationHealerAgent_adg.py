"""ADG importability contract for agentic_core/L5_safety/reasoning/LocationHealerAgent.py."""
from __future__ import annotations

import agentic_core.L5_safety.reasoning.LocationHealerAgent  # noqa: F401


def test_module_importable():
    """Module LocationHealerAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.LocationHealerAgent is not None
