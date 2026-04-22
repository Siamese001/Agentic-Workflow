"""Smoke tests for vllm_gateway_integration_types exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestVllmGatewayIntegrationTypes:
    """Smoke tests for vllm_gateway_integration_types exports."""

    def test_vllm_gateway_integration_types_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "vllm_gateway_integration_types")
        assert module is not None

    def test_vllm_gateway_integration_types_class(self) -> None:
        """Import the class export."""
        klass = import_attr_or_skip("agentic_core", "VllmGatewayIntegrationTypes")
        assert klass is not None

    def test_vllm_gateway_integration_types_callable(self) -> None:
        """Import the validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_vllm_gateway_integration_types")
        assert callable(validator)
