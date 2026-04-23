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

from contextlib import contextmanager
from typing import Any, Iterator, Mapping

from opentelemetry import trace

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
                except (
                    AttributeError,
                    TypeError,
                ):  # guardian: allow-log-and-swallow -- span attr is best-effort telemetry
                    pass
        yield span


__all__ = ["sl_span"]
