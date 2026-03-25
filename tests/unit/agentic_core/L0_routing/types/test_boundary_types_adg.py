"""ADG importability contract for agentic_core/L0_routing/types/boundary_types.py."""
from __future__ import annotations

import agentic_core.L0_routing.types.boundary_types  # noqa: F401


def test_module_importable():
    """Module boundary_types must be importable."""
    assert agentic_core.L0_routing.types.boundary_types is not None
