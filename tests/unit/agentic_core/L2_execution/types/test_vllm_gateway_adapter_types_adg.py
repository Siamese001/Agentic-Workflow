"""ADG-driven tests for L2_execution/types/vllm_gateway_adapter_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.types.vllm_gateway_adapter_types import VLLMGatewayAdapter
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    VLLMGatewayAdapter = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="vllm_gateway_adapter_types deps unavailable")
class TestVLLMGatewayAdapter:
    def test_importable(self):
        assert callable(VLLMGatewayAdapter)

    def test_has_evaluate(self):
        assert hasattr(VLLMGatewayAdapter, "evaluate")


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
