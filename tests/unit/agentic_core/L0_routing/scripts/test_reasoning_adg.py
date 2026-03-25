"""ADG importability contract for agentic_core/L0_routing/scripts/reasoning.py."""
from __future__ import annotations

import agentic_core.L0_routing.scripts.reasoning  # noqa: F401


def test_module_importable():
    """Module reasoning must be importable."""
    assert agentic_core.L0_routing.scripts.reasoning is not None
