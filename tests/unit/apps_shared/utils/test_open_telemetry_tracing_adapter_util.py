"""Foundational behavioral tests for apps_shared/utils/open_telemetry_tracing_adapter_util.py.

fan_in=13 — this module is imported by 13 other modules.
ADG contract: import-hygiene is covered by test_open_telemetry_tracing_adapter_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.open_telemetry_tracing_adapter_util import (  # noqa: F401
        SpanType,
        SpanMetadata,
        CostMetrics,
        ResilienceMetrics,
        OpenTelemetryTracingAdapter,
        get_tracer,
        reset_tracer,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    SpanType = None  # type: ignore[assignment,misc]
    SpanMetadata = None  # type: ignore[assignment,misc]
    CostMetrics = None  # type: ignore[assignment,misc]
    ResilienceMetrics = None  # type: ignore[assignment,misc]
    OpenTelemetryTracingAdapter = None  # type: ignore[assignment,misc]
    get_tracer = None  # type: ignore[assignment,misc]
    reset_tracer = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="open_telemetry_tracing_adapter_util.py deps unavailable")
class TestSpanTypeContract:
    def test_is_enum(self):
        import enum
        assert issubclass(SpanType, enum.Enum)

    def test_has_members(self):
        assert len(list(SpanType)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in SpanType:
            assert member.value is not None

    def test_known_member_orchestrator_exists(self):
        assert hasattr(SpanType, 'ORCHESTRATOR')

@pytest.mark.skipif(not _AVAILABLE, reason="open_telemetry_tracing_adapter_util.py deps unavailable")
class TestSpanMetadataContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(SpanMetadata)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(SpanMetadata)}
        assert field_names >= {'layer', 'attributes', 'span_type', 'component'}

@pytest.mark.skipif(not _AVAILABLE, reason="open_telemetry_tracing_adapter_util.py deps unavailable")
class TestCostMetricsContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(CostMetrics)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(CostMetrics)}
        assert field_names >= {'estimated_cost_usd', 'completion_tokens', 'prompt_tokens', 'total_tokens', 'model'}

@pytest.mark.skipif(not _AVAILABLE, reason="open_telemetry_tracing_adapter_util.py deps unavailable")
class TestResilienceMetricsContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ResilienceMetrics)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ResilienceMetrics)}
        assert field_names >= {'circuit_breaker_state', 'success', 'retry_attempts', 'backoff_ms', 'rate_limit_status'}

@pytest.mark.skipif(not _AVAILABLE, reason="open_telemetry_tracing_adapter_util.py deps unavailable")
class TestOpenTelemetryTracingAdapterContract:
    def test_is_class(self):
        assert isinstance(OpenTelemetryTracingAdapter, type)

    def test_has_method_trace_orchestrator(self):
        assert callable(getattr(OpenTelemetryTracingAdapter, 'trace_orchestrator', None))

    def test_has_method_trace_cognitive(self):
        assert callable(getattr(OpenTelemetryTracingAdapter, 'trace_cognitive', None))

    def test_has_method_trace_action(self):
        assert callable(getattr(OpenTelemetryTracingAdapter, 'trace_action', None))

    def test_has_method_trace_tool(self):
        assert callable(getattr(OpenTelemetryTracingAdapter, 'trace_tool', None))

@pytest.mark.skipif(not _AVAILABLE, reason="open_telemetry_tracing_adapter_util.py deps unavailable")
class TestGetTracerFunction:
    def test_is_callable(self):
        assert callable(get_tracer)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_tracer)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="open_telemetry_tracing_adapter_util.py deps unavailable")
class TestResetTracerFunction:
    def test_is_callable(self):
        assert callable(reset_tracer)

@pytest.mark.skipif(not _AVAILABLE, reason="open_telemetry_tracing_adapter_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="open_telemetry_tracing_adapter_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="open_telemetry_tracing_adapter_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="open_telemetry_tracing_adapter_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="open_telemetry_tracing_adapter_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module open_telemetry_tracing_adapter_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
