"""Smoke tests for vllm_gateway_adapter exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestVllmGatewayAdapter:
    """Smoke tests for vllm_gateway_adapter exports."""

    def test_vllm_gateway_adapter_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "vllm_gateway_adapter")
        assert module is not None

    def test_vllm_gateway_adapter_class(self) -> None:
        """Import the class export."""
        klass = import_attr_or_skip("agentic_core", "VllmGatewayAdapter")
        assert klass is not None

    def test_vllm_gateway_adapter_callable(self) -> None:
        """Import the validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_vllm_gateway_adapter")
        assert callable(validator)
