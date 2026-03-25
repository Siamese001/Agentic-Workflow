"""ADG importability contract for agentic_core/L2_execution/protocol.py."""
from __future__ import annotations

import agentic_core.L2_execution.protocol  # noqa: F401


def test_module_importable():
    """Module protocol must be importable."""
    assert agentic_core.L2_execution.protocol is not None
