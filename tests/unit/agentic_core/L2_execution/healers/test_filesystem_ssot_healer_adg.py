"""ADG importability contract for agentic_core/L2_execution/healers/filesystem_ssot_healer.py."""
from __future__ import annotations

import agentic_core.L2_execution.healers.filesystem_ssot_healer  # noqa: F401


def test_module_importable():
    """Module filesystem_ssot_healer must be importable."""
    assert agentic_core.L2_execution.healers.filesystem_ssot_healer is not None
