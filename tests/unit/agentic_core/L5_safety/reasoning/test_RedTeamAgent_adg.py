"""ADG importability contract for agentic_core/L5_safety/reasoning/RedTeamAgent.py."""
from __future__ import annotations

import agentic_core.L5_safety.reasoning.RedTeamAgent  # noqa: F401


def test_module_importable():
    """Module RedTeamAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.RedTeamAgent is not None
