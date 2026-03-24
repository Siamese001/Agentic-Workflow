"""ADG importability contract for agentic_core/L2_execution/types/vllm_gateway_integration_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_vllm_gateway_integration_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.types.vllm_gateway_integration_types import (  # noqa: F401
        VLLMCircuitBreakerRegistry,
        VLLMGatewayTelemetry,
        VLLMLocalRequest,
        VLLMQueueController,
        select_serving_profile,
        shape_local_request,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    select_serving_profile = None  # type: ignore[assignment,misc]
    VLLMLocalRequest = None  # type: ignore[assignment,misc]
    shape_local_request = None  # type: ignore[assignment,misc]
    VLLMQueueController = None  # type: ignore[assignment,misc]
    VLLMCircuitBreakerRegistry = None  # type: ignore[assignment,misc]
    VLLMGatewayTelemetry = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="vllm_gateway_integration_types deps unavailable")
class TestVllmGatewayIntegrationTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/types/vllm_gateway_integration_types.py must be importable."""
        assert _AVAILABLE

    def test_vllmlocalrequest_defined(self) -> None:
        assert VLLMLocalRequest is not None

    def test_vllmqueuecontroller_defined(self) -> None:
        assert VLLMQueueController is not None

    def test_vllmcircuitbreakerregistry_defined(self) -> None:
        assert VLLMCircuitBreakerRegistry is not None

    def test_vllmgatewaytelemetry_defined(self) -> None:
        assert VLLMGatewayTelemetry is not None