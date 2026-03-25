"""ADG importability contract for agentic_core/L2_execution/healers/gravity_leak_healer.py."""
from __future__ import annotations

import agentic_core.L2_execution.healers.gravity_leak_healer  # noqa: F401


def test_module_importable():
    """Module gravity_leak_healer must be importable."""
    assert agentic_core.L2_execution.healers.gravity_leak_healer is not None
