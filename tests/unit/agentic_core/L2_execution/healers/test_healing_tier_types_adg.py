"""ADG importability contract for agentic_core/L2_execution/healers/healing_tier_types.py."""
from __future__ import annotations

import agentic_core.L2_execution.healers.healing_tier_types  # noqa: F401


def test_module_importable():
    """Module healing_tier_types must be importable."""
    assert agentic_core.L2_execution.healers.healing_tier_types is not None
