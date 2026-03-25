"""ADG importability contract for agentic_core/L2_execution/healers/healing_provider_adapters.py."""
from __future__ import annotations

import agentic_core.L2_execution.healers.healing_provider_adapters  # noqa: F401


def test_module_importable():
    """Module healing_provider_adapters must be importable."""
    assert agentic_core.L2_execution.healers.healing_provider_adapters is not None
