"""ADG importability contract for agentic_core/L0_routing/seams/layer_emission_seam.py."""
from __future__ import annotations

import agentic_core.L0_routing.seams.layer_emission_seam  # noqa: F401


def test_module_importable():
    """Module layer_emission_seam must be importable."""
    assert agentic_core.L0_routing.seams.layer_emission_seam is not None
