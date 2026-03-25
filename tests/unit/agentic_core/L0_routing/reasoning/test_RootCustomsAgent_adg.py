"""ADG importability contract for agentic_core/L0_routing/reasoning/RootCustomsAgent.py."""
from __future__ import annotations

import agentic_core.L0_routing.reasoning.RootCustomsAgent  # noqa: F401


def test_module_importable():
    """Module RootCustomsAgent must be importable."""
    assert agentic_core.L0_routing.reasoning.RootCustomsAgent is not None
