"""OTEL bootstrap for the proof harness.

Configures a real OpenTelemetry tracer + exporter when the SDK is
installed and ``OTEL_EXPORTER_OTLP_ENDPOINT`` is set. Falls back to an
in-memory ``InMemorySpanExporter`` when only the SDK is present (so
spans are still real OTEL spans — just exported to memory rather than a
collector). Reports honestly when nothing is configured.

Public surface:

    setup_tracer(service_name="proof_harness") -> BootstrapResult

The harness uses ``BootstrapResult.tracer`` to create real spans, then
reads ``BootstrapResult.exporter_status`` to populate the
``otel_telemetry`` layer receipt.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any


@dataclass
class BootstrapResult:
    """OTEL setup status returned to the harness."""

    sdk_importable: bool = False
    tracer: Any = None
    exporter_status: str = "NOT_IMPLEMENTED"
    collector_endpoint: str | None = None
    in_memory_exporter: Any = None
    error: str | None = None
    spans_collected: list[dict[str, Any]] = field(default_factory=list)

    @property
    def is_real(self) -> bool:
        return self.sdk_importable and self.tracer is not None


def setup_tracer(service_name: str = "proof_harness") -> BootstrapResult:
    """Initialise a real OTEL tracer + exporter where possible."""
    result = BootstrapResult()
    try:
        from opentelemetry import trace  # noqa: PLC0415
        from opentelemetry.sdk.resources import Resource  # noqa: PLC0415
        from opentelemetry.sdk.trace import TracerProvider  # noqa: PLC0415
        from opentelemetry.sdk.trace.export import BatchSpanProcessor  # noqa: PLC0415
    except ImportError as exc:
        result.error = (
            f"opentelemetry SDK not importable: {exc!r}. "
            "Install: pip install opentelemetry-sdk opentelemetry-exporter-otlp"
        )
        return result

    result.sdk_importable = True
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    result.collector_endpoint = endpoint

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)

    if endpoint:
        try:
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import (  # noqa: PLC0415
                OTLPSpanExporter,
            )
            provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
            result.exporter_status = f"otlp_http:{endpoint}"
        except ImportError:
            try:
                from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (  # noqa: PLC0415
                    OTLPSpanExporter as GrpcOTLPSpanExporter,
                )
                provider.add_span_processor(BatchSpanProcessor(GrpcOTLPSpanExporter()))
                result.exporter_status = f"otlp_grpc:{endpoint}"
            except ImportError as exc:
                result.exporter_status = f"sdk_only_no_exporter: {exc!r}"

    # Always attach an in-memory exporter for local verification.
    try:
        from opentelemetry.sdk.trace.export.in_memory_span_exporter import (  # noqa: PLC0415
            InMemorySpanExporter,
        )
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor  # noqa: PLC0415
        in_mem = InMemorySpanExporter()
        provider.add_span_processor(SimpleSpanProcessor(in_mem))
        result.in_memory_exporter = in_mem
        if not endpoint:
            result.exporter_status = "in_memory_only"
    except ImportError as exc:
        if not endpoint:
            result.exporter_status = f"sdk_only_no_in_memory: {exc!r}"

    trace.set_tracer_provider(provider)
    result.tracer = trace.get_tracer(service_name)
    return result


def collect_in_memory_spans(result: BootstrapResult) -> list[dict[str, Any]]:
    """Drain the in-memory exporter and return JSON-friendly span dicts."""
    if result.in_memory_exporter is None:
        return []
    spans = result.in_memory_exporter.get_finished_spans()
    out: list[dict[str, Any]] = []
    for sp in spans:
        ctx = sp.get_span_context()
        parent = sp.parent
        out.append({
            "trace_id": format(ctx.trace_id, "032x"),
            "span_id": format(ctx.span_id, "016x"),
            "parent_span_id": (
                format(parent.span_id, "016x") if parent else None
            ),
            "name": sp.name,
            "kind": str(sp.kind),
            "start_time_ns": sp.start_time,
            "end_time_ns": sp.end_time,
            "status_code": str(sp.status.status_code),
            "attributes": dict(sp.attributes or {}),
        })
    return out


__all__ = ["BootstrapResult", "setup_tracer", "collect_in_memory_spans"]
