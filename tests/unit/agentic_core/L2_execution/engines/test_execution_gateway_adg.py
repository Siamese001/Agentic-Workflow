"""ADG importability contract for agentic_core/L2_execution/engines/execution_gateway.py."""
from __future__ import annotations

import agentic_core.L2_execution.engines.execution_gateway  # noqa: F401


def test_module_importable():
    """Module execution_gateway must be importable."""
    assert agentic_core.L2_execution.engines.execution_gateway is not None
