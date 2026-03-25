"""ADG importability contract for agentic_core/L0_routing/seams/canonical_truth_seam.py."""
from __future__ import annotations

import agentic_core.L0_routing.seams.canonical_truth_seam  # noqa: F401


def test_module_importable():
    """Module canonical_truth_seam must be importable."""
    assert agentic_core.L0_routing.seams.canonical_truth_seam is not None
