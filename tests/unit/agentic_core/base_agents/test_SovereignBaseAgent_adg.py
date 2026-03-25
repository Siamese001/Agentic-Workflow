"""ADG importability contract for agentic_core/base_agents/SovereignBaseAgent.py."""
from __future__ import annotations

import agentic_core.base_agents.SovereignBaseAgent  # noqa: F401


def test_module_importable():
    """Module SovereignBaseAgent must be importable."""
    assert agentic_core.base_agents.SovereignBaseAgent is not None
