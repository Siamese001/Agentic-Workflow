"""ADG importability contract for agentic_core/L0_routing/types/routing_config_seal_types.py."""
from __future__ import annotations

import agentic_core.L0_routing.types.routing_config_seal_types  # noqa: F401


def test_module_importable():
    """Module routing_config_seal_types must be importable."""
    assert agentic_core.L0_routing.types.routing_config_seal_types is not None
