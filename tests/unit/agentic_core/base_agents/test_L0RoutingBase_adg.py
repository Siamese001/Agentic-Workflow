"""ADG importability contract for agentic_core/base_agents/L0RoutingBase.py."""
from __future__ import annotations

import agentic_core.base_agents.L0RoutingBase  # noqa: F401


def test_module_importable():
    """Module L0RoutingBase must be importable."""
    assert agentic_core.base_agents.L0RoutingBase is not None
