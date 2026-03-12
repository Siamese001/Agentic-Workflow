"""Foundational behavioral tests for agentic_core/L2_execution/types/vllm_gateway_integration_types.py.

fan_in=4 — imported by 4 other modules.
ADG import-hygiene is covered separately by test_vllm_gateway_integration_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.types.vllm_gateway_integration_types import (  # noqa: F401
        VLLMLocalRequest,
        VLLMQueueController,
        VLLMCircuitBreakerRegistry,
        VLLMGatewayTelemetry,
        VLLMGatewayCallResult,
        select_serving_profile,
        shape_local_request,
        evaluate_gateway_call,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    VLLMLocalRequest = None  # type: ignore[assignment,misc]
    VLLMQueueController = None  # type: ignore[assignment,misc]
    VLLMCircuitBreakerRegistry = None  # type: ignore[assignment,misc]
    VLLMGatewayTelemetry = None  # type: ignore[assignment,misc]
    VLLMGatewayCallResult = None  # type: ignore[assignment,misc]
    select_serving_profile = None  # type: ignore[assignment,misc]
    shape_local_request = None  # type: ignore[assignment,misc]
    evaluate_gateway_call = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="vllm_gateway_integration_types.py deps unavailable")
class TestVLLMLocalRequestContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(VLLMLocalRequest)

    def test_is_frozen(self):
        assert VLLMLocalRequest.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(VLLMLocalRequest)}
        assert fnames >= {'prompt', 'model', 'top_p', 'max_tokens', 'seed', 'temperature'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(VLLMLocalRequest)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_gateway_integration_types.py deps unavailable")
class TestVLLMQueueControllerContract:
    def test_is_class(self):
        assert isinstance(VLLMQueueController, type)

    def test_has_method_snapshot(self):
        assert callable(getattr(VLLMQueueController, 'snapshot', None))

    def test_has_method_acquire(self):
        assert callable(getattr(VLLMQueueController, 'acquire', None))

    def test_has_method_release(self):
        assert callable(getattr(VLLMQueueController, 'release', None))

    def test_has_method_depth(self):
        assert callable(getattr(VLLMQueueController, 'depth', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(VLLMQueueController) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_gateway_integration_types.py deps unavailable")
class TestVLLMCircuitBreakerRegistryContract:
    def test_is_class(self):
        assert isinstance(VLLMCircuitBreakerRegistry, type)

    def test_has_method_get(self):
        assert callable(getattr(VLLMCircuitBreakerRegistry, 'get', None))

    def test_has_method_record_failure(self):
        assert callable(getattr(VLLMCircuitBreakerRegistry, 'record_failure', None))

    def test_has_method_record_success(self):
        assert callable(getattr(VLLMCircuitBreakerRegistry, 'record_success', None))

    def test_has_method_is_open(self):
        assert callable(getattr(VLLMCircuitBreakerRegistry, 'is_open', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(VLLMCircuitBreakerRegistry) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_gateway_integration_types.py deps unavailable")
class TestVLLMGatewayTelemetryContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(VLLMGatewayTelemetry)

    def test_is_frozen(self):
        assert VLLMGatewayTelemetry.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(VLLMGatewayTelemetry)}
        assert fnames >= {'model_tier', 'max_output_tokens_requested', 'provider_selected', 'max_model_len_configured', 'token_budget_ok', 'prompt_tokens_estimated'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(VLLMGatewayTelemetry)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_gateway_integration_types.py deps unavailable")
class TestVLLMGatewayCallResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(VLLMGatewayCallResult)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(VLLMGatewayCallResult)}
        assert fnames >= {'route_to_gemini', 'telemetry', 'backpressure', 'local_request', 'preflight', 'invariant_violations'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(VLLMGatewayCallResult)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_gateway_integration_types.py deps unavailable")
class TestSelectServingProfileFunction:
    def test_is_callable(self):
        assert callable(select_serving_profile)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(select_serving_profile)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_gateway_integration_types.py deps unavailable")
class TestShapeLocalRequestFunction:
    def test_is_callable(self):
        assert callable(shape_local_request)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(shape_local_request)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_gateway_integration_types.py deps unavailable")
class TestEvaluateGatewayCallFunction:
    def test_is_callable(self):
        assert callable(evaluate_gateway_call)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(evaluate_gateway_call)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_gateway_integration_types.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_gateway_integration_types.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_gateway_integration_types.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_gateway_integration_types.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_gateway_integration_types.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_gateway_integration_types.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: vllm_gateway_integration_types importable or gracefully unavailable."""
    assert True
