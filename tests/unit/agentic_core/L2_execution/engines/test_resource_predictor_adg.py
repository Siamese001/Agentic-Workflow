"""ADG importability contract for agentic_core/L2_execution/engines/resource_predictor.py."""
from __future__ import annotations

import agentic_core.L2_execution.engines.resource_predictor  # noqa: F401


def test_module_importable():
    """Module resource_predictor must be importable."""
    assert agentic_core.L2_execution.engines.resource_predictor is not None
