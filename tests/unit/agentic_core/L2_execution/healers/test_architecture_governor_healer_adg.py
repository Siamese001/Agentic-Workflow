"""ADG importability contract for agentic_core/L2_execution/healers/architecture_governor_healer.py."""
from __future__ import annotations

import agentic_core.L2_execution.healers.architecture_governor_healer  # noqa: F401


def test_module_importable():
    """Module architecture_governor_healer must be importable."""
    assert agentic_core.L2_execution.healers.architecture_governor_healer is not None
