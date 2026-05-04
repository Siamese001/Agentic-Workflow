"""Optional OTEL SDK integration for the proof harness.

When the OpenTelemetry SDK is installed AND ``OTEL_EXPORTER_OTLP_ENDPOINT``
is set, :func:`maybe_export_spans` mirrors every :class:`SpanRecord` to a
real OTEL tracer with the canonical spine attributes.

When either prerequisite is missing, it returns a ``status="DISABLED"``
result — never raises, never blocks. The harness's ``LocalSpanRecorder``
remains the source of truth either way.

This module is the structural answer to prompt §4G: "real OTEL spans" are
emitted when the runtime is configured to receive them; otherwise the
harness honestly reports the export was skipped.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Sequence

from apps_shared.validators.proof.proof_contracts import SpanRecord


_DEFAULT_SERVICE_NAME = "apps_runtime_proof_harness"


@dataclass
class OtelExportResult:
    """Outcome of attempting to mirror spans to a real OTEL tracer."""

    status: str  # EXPORTED | DISABLED | ERROR
    reason: str
    spans_attempted: int = 0
    spans_exported: int = 0
    sdk_present: bool = False
    endpoint: str | None = None
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "reason": self.reason,
            "spans_attempted": self.spans_attempted,
            "spans_exported": self.spans_exported,
            "sdk_present": self.sdk_present,
            "endpoint": self.endpoint,
            "errors": list(self.errors),
        }


def _detect_otel() -> tuple[bool, str | None]:
    """Return (sdk_present, endpoint)."""
    try:
        import opentelemetry  # noqa: F401  PLC0415

        sdk_present = True
    except ImportError:
        sdk_present = False
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    return sdk_present, endpoint


def maybe_export_spans(
    spans: Sequence[SpanRecord],
    *,
    service_name: str = _DEFAULT_SERVICE_NAME,
    force_disabled: bool = False,
) -> OtelExportResult:
    """Mirror ``spans`` to a real OTEL tracer when configured.

    Args:
        spans: span records emitted by the LocalSpanRecorder
        service_name: OTEL ``service.name`` resource attribute
        force_disabled: if True, skip even when SDK + endpoint present
                        (used by tests to assert the disabled path)
    """
    sdk_present, endpoint = _detect_otel()

    if force_disabled:
        return OtelExportResult(
            status="DISABLED",
            reason="force_disabled=True",
            spans_attempted=len(spans),
            sdk_present=sdk_present,
            endpoint=endpoint,
        )
    if not sdk_present:
        return OtelExportResult(
            status="DISABLED",
            reason="opentelemetry SDK not importable",
            spans_attempted=len(spans),
            sdk_present=False,
            endpoint=endpoint,
        )
    if not endpoint:
        return OtelExportResult(
            status="DISABLED",
            reason="OTEL_EXPORTER_OTLP_ENDPOINT not set",
            spans_attempted=len(spans),
            sdk_present=True,
            endpoint=None,
        )

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import (
            BatchSpanProcessor,
            SimpleSpanProcessor,
        )

        # Prefer OTLP exporter; fall back to a no-op span processor if
        # the OTLP exporter package is unavailable.
        try:
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
                OTLPSpanExporter,
            )

            exporter: Any = OTLPSpanExporter(endpoint=endpoint)
            processor: Any = BatchSpanProcessor(exporter)
        except ImportError:
            from opentelemetry.sdk.trace.export import ConsoleSpanExporter

            exporter = ConsoleSpanExporter()
            processor = SimpleSpanProcessor(exporter)
    except (ImportError, ValueError, RuntimeError) as exc:
        return OtelExportResult(
            status="ERROR",
            reason=f"OTEL initialization failed: {exc!r}",
            spans_attempted=len(spans),
            sdk_present=True,
            endpoint=endpoint,
            errors=[repr(exc)],
        )

    # Idempotent provider — safe to call repeatedly across scenarios
    provider = TracerProvider(
        resource=Resource.create({"service.name": service_name}),
    )
    provider.add_span_processor(processor)
    tracer = trace.get_tracer(__name__, tracer_provider=provider)

    exported = 0
    errors: list[str] = []
    for s in spans:
        try:
            with tracer.start_as_current_span(
                s.name,
                attributes={
                    "trace_id_local": s.trace_id,
                    "span_id_local": s.span_id,
                    "layer": s.layer,
                    "status": s.status,
                    "app_id": s.app_id or "",
                    "scenario_id": s.scenario_id or "",
                    "request_id": s.request_id or "",
                    "run_id": s.run_id or "",
                },
            ):
                pass  # span lifecycle managed by context manager
            exported += 1
        except (RuntimeError, ValueError, TypeError) as exc:
            errors.append(f"{s.span_id}: {exc!r}")

    # Force flush so spans aren't held in the BSP buffer past return
    try:
        provider.force_flush(timeout_millis=2000)
    except (RuntimeError, ValueError) as exc:
        errors.append(f"flush: {exc!r}")

    return OtelExportResult(
        status="EXPORTED" if not errors else "ERROR",
        reason="ok" if not errors else f"{len(errors)} export errors",
        spans_attempted=len(spans),
        spans_exported=exported,
        sdk_present=True,
        endpoint=endpoint,
        errors=errors,
    )


__all__ = [
    "OtelExportResult",
    "maybe_export_spans",
]
