"""ADG importability contract for agentic_core/L2_execution/enforcement/SovereignLLMGateway.py."""
from __future__ import annotations

import agentic_core.L2_execution.enforcement.SovereignLLMGateway  # noqa: F401


def test_module_importable():
    """Module SovereignLLMGateway must be importable."""
    assert agentic_core.L2_execution.enforcement.SovereignLLMGateway is not None
