"""ADG importability contract for agentic_core/L0_routing/seams/vigilance_seam.py."""
from __future__ import annotations

import agentic_core.L0_routing.seams.vigilance_seam  # noqa: F401


def test_module_importable():
    """Module vigilance_seam must be importable."""
    assert agentic_core.L0_routing.seams.vigilance_seam is not None
