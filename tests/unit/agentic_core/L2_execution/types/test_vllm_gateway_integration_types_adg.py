"""ADG importability contract for agentic_core/L2_execution/types/vllm_gateway_integration_types.py."""
from __future__ import annotations

import agentic_core.L2_execution.types.vllm_gateway_integration_types  # noqa: F401


def test_module_importable():
    """Module vllm_gateway_integration_types must be importable."""
    assert agentic_core.L2_execution.types.vllm_gateway_integration_types is not None
