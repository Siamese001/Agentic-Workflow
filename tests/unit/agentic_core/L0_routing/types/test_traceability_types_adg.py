"""ADG importability contract for agentic_core/L0_routing/types/traceability_types.py."""
from __future__ import annotations

import agentic_core.L0_routing.types.traceability_types  # noqa: F401


def test_module_importable():
    """Module traceability_types must be importable."""
    assert agentic_core.L0_routing.types.traceability_types is not None
