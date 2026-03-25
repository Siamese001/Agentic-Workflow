"""ADG importability contract for agentic_core/L0_routing/scripts/full_agent_discovery.py."""
from __future__ import annotations

import agentic_core.L0_routing.scripts.full_agent_discovery  # noqa: F401


def test_module_importable():
    """Module full_agent_discovery must be importable."""
    assert agentic_core.L0_routing.scripts.full_agent_discovery is not None
