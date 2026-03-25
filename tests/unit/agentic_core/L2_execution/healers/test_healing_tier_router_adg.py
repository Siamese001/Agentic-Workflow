"""ADG importability contract for agentic_core/L2_execution/healers/healing_tier_router.py."""
from __future__ import annotations

import agentic_core.L2_execution.healers.healing_tier_router  # noqa: F401


def test_module_importable():
    """Module healing_tier_router must be importable."""
    assert agentic_core.L2_execution.healers.healing_tier_router is not None
