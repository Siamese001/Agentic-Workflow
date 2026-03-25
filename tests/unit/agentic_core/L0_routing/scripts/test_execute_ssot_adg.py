"""ADG importability contract for agentic_core/L0_routing/scripts/execute_ssot.py."""
from __future__ import annotations

import agentic_core.L0_routing.scripts.execute_ssot  # noqa: F401


def test_module_importable():
    """Module execute_ssot must be importable."""
    assert agentic_core.L0_routing.scripts.execute_ssot is not None
