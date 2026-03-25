"""ADG importability contract for agentic_core/L0_routing/scripts/chunk_type.py."""
from __future__ import annotations

import agentic_core.L0_routing.scripts.chunk_type  # noqa: F401


def test_module_importable():
    """Module chunk_type must be importable."""
    assert agentic_core.L0_routing.scripts.chunk_type is not None
