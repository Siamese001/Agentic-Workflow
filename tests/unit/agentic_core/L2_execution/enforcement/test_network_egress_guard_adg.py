"""ADG importability contract for agentic_core/L2_execution/enforcement/network_egress_guard.py."""
from __future__ import annotations

import agentic_core.L2_execution.enforcement.network_egress_guard  # noqa: F401


def test_module_importable():
    """Module network_egress_guard must be importable."""
    assert agentic_core.L2_execution.enforcement.network_egress_guard is not None
