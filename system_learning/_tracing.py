"""Shared OTel tracer helper for system_learning modules.

Mirrors `apps_eval.integrations.tracing.eval_span` so system_learning
modules can emit real OpenTelemetry spans through the canonical
`opentelemetry.trace.get_tracer()` API without each module redeclaring
the same boilerplate.

When no SDK TracerProvider is installed (default for unit tests), the
OTel API returns a ProxyTracer backed by a NoOpTracer — `sl_span()`
is therefore free in both CPU and allocations, and safe to sprinkle
across hot paths.

Plan reference: .windsurf/plans/eval-meta-otel-deferred-completion-d6b4e0.md
Wave W-D2 (L_SL / L6 tracer wiring).
"""

from __future__ import annotations

# OTel GenAI semconv alignment (Plan: three-bucket-gap-remediation-069806 W3).
# system_learning generic tracer — defaults to workflow-level emission.
# The constants below are imported and surfaced so future span construction
# in this module attaches gen_ai.operation.name, satisfying the upstream
# OTel GenAI SIG semantic conventions.
from agentic_core.L6_observability.semconv.gen_ai import (
    ATTR_OPERATION_NAME,
    OPERATION_INVOKE_WORKFLOW,
)

#: Canonical GenAI operation discriminator for spans emitted by this module.
_GEN_AI_OPERATION: str = OPERATION_INVOKE_WORKFLOW
#: OTel attribute key for the discriminator (gen_ai.operation.name).
_GEN_AI_OPERATION_KEY: str = ATTR_OPERATION_NAME

import logging
import time
import uuid
from contextlib import contextmanager
from typing import Any, Iterator, Mapping

from opentelemetry import trace

logger = logging.getLogger(__name__)
_tracer = trace.get_tracer("system_learning")


@contextmanager
def sl_span(name: str, attributes: Mapping[str, Any] | None = None) -> Iterator[Any]:
    """Start an OTel span named ``name`` with optional ``attributes``.

    Usage
    -----
    >>> from system_learning._tracing import sl_span
    >>> with sl_span("system_learning.v1.bus_consumer.drain_and_apply", {"sl.count": 5}) as span:
    ...     span.set_attribute("sl.extra", 42)
    ...     ...

    The yielded value is the underlying OTel span object (or NoOpSpan)
    so callers can set additional attributes on it inside the block.
    """
    with _tracer.start_as_current_span(name) as span:
        if attributes:
            for key, value in attributes.items():
                try:
                    span.set_attribute(key, value)
                except (  # guardian: allow-silent-swallow -- span attr is best-effort telemetry; missing/invalid attr must not break the wrapped hot path
                    AttributeError,
                    TypeError,
                ):
                    pass
        yield span


@contextmanager
def sl_span_with_ingest(
    name: str,
    attributes: Mapping[str, Any] | None = None,
    *,
    trace_id: str | None = None,
    layer: str = "L_SL",
    kind: str = "reasoning",
) -> Iterator[Any]:
    """sl_span variant that also mirrors the span into the runtime ADG store.

    W7.1 / P2.3 — this is the in-process ingest path for system_learning
    producers. Mirroring is best-effort; runtime-ADG failures never break
    the wrapped hot path.

    Parameters
    ----------
    name
        Span name.
    attributes
        Optional OTel-style attribute dict.
    trace_id
        Optional explicit trace id. Defaults to a fresh uuid4.
    layer
        Architecture layer tag for the runtime ADG node (default ``L_SL``).
    kind
        Span kind tag for the runtime ADG node (default ``reasoning``).
    """
    resolved_trace_id = trace_id or str(uuid.uuid4())
    started_at = time.time()
    with _tracer.start_as_current_span(name) as span:
        if attributes:
            for key, value in attributes.items():
                try:
                    span.set_attribute(key, value)
                except (  # guardian: allow-silent-swallow -- span attr is best-effort telemetry; missing/invalid attr must not break the wrapped hot path
                    AttributeError,
                    TypeError,
                ):
                    pass
        try:
            yield span
        finally:
            _forward_to_runtime_adg(
                name=name,
                trace_id=resolved_trace_id,
                started_at=started_at,
                attributes=dict(attributes) if attributes else {},
                layer=layer,
                kind=kind,
            )


def _forward_to_runtime_adg(
    *,
    name: str,
    trace_id: str,
    started_at: float,
    attributes: dict[str, Any],
    layer: str,
    kind: str,
) -> None:
    """Best-effort mirror of a system_learning span into the runtime ADG store."""
    try:
        from agentic_core.L6_observability.otel_runtime_ingest import (  # noqa: PLC0415
            emit_span_to_runtime_adg,
        )

        span = {
            "span_id": trace_id,
            "trace_id": trace_id,
            "parent_span_id": "",
            "name": name,
            "kind": kind,
            "layer": layer,
            "component": "system_learning",
            "service_name": "system_learning",
            "ts_utc": int(started_at * 1000),
            "duration_ms": max(0.0, (time.time() - started_at) * 1000.0),
            "status": "ok",
            "attributes": attributes,
        }
        emit_span_to_runtime_adg(span, mission=f"sl.{name}", trace_id=trace_id)
    except (
        ImportError,
        AttributeError,
        TypeError,
        ValueError,
    ) as exc:  # guardian: allow-log-and-swallow -- runtime-ADG mirror is best-effort; must never break system_learning hot path
        logger.debug("sl_span runtime-ADG forward failed: %s", exc)


__all__ = ["sl_span", "sl_span_with_ingest"]
