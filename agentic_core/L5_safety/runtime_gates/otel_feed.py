"""Live OTEL → ``BaselineRegistry`` feed for G25 RuntimeAnomaly.

Subscribes to a stream of completed OTEL spans and pushes observations
into the registry so baselines stay fresh without re-bootstrap.

Standard OTEL semantic conventions used by ``default_span_extractor``:
- ``task.class``                     -> task_class label (custom convention)
- ``gen_ai.usage.input_tokens`` +
  ``gen_ai.usage.output_tokens``     -> ``tokens``
- ``gen_ai.cost.usd``                -> ``cost_usd``
- ``duration_ms`` or computed from
  ``end_time_ns - start_time_ns``    -> ``latency_ms``
- ``mcp.tool.invocations`` (count)   -> ``tool_count``
- ``retry.count``                    -> ``retry_count``
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterable
from typing import Any

from agentic_core.L5_safety.runtime_gates.baseline_registry import (
    TRACKED_METRICS,
    BaselineRegistry,
)

logger = logging.getLogger(__name__)


SpanExtractor = Callable[[dict[str, Any]], "tuple[str, dict[str, float]] | None"]


def _attr(span: dict[str, Any], key: str) -> Any:
    """Read an attribute from either ``span['attributes']`` or top-level."""
    attrs = span.get("attributes") or {}
    if isinstance(attrs, dict) and key in attrs:
        return attrs[key]
    return span.get(key)


def _coerce_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def default_span_extractor(span: dict[str, Any]) -> tuple[str, dict[str, float]] | None:
    """Map an OTEL span dict to ``(task_class, observation)`` or None.

    Returns None if no ``task_class`` or no extractable metrics.
    """
    task_class = _attr(span, "task.class") or _attr(span, "task_class")
    if not task_class or not isinstance(task_class, str):
        return None

    observation: dict[str, float] = {}

    # tokens — sum input + output if present
    input_tokens = _coerce_float(_attr(span, "gen_ai.usage.input_tokens"))
    output_tokens = _coerce_float(_attr(span, "gen_ai.usage.output_tokens"))
    if input_tokens is not None or output_tokens is not None:
        observation["tokens"] = (input_tokens or 0.0) + (output_tokens or 0.0)
    else:
        # Fallback to a flat ``tokens`` field
        flat_tokens = _coerce_float(_attr(span, "tokens"))
        if flat_tokens is not None:
            observation["tokens"] = flat_tokens

    # cost
    cost = _coerce_float(_attr(span, "gen_ai.cost.usd"))
    if cost is None:
        cost = _coerce_float(_attr(span, "cost_usd"))
    if cost is not None:
        observation["cost_usd"] = cost

    # latency
    latency = _coerce_float(_attr(span, "duration_ms")) or _coerce_float(_attr(span, "latency_ms"))
    if latency is None:
        start = _coerce_float(span.get("start_time_ns"))
        end = _coerce_float(span.get("end_time_ns"))
        if start is not None and end is not None and end >= start:
            latency = (end - start) / 1_000_000.0  # ns -> ms
    if latency is not None:
        observation["latency_ms"] = latency

    # tool count
    tool_count = _coerce_float(_attr(span, "mcp.tool.invocations")) or _coerce_float(
        _attr(span, "tool_count")
    )
    if tool_count is not None:
        observation["tool_count"] = tool_count

    # retry count
    retry_count = _coerce_float(_attr(span, "retry.count")) or _coerce_float(_attr(span, "retry_count"))
    if retry_count is not None:
        observation["retry_count"] = retry_count

    if not observation:
        return None
    # Drop any keys that aren't tracked (defensive — should never fire here).
    observation = {k: v for k, v in observation.items() if k in TRACKED_METRICS}
    if not observation:
        return None
    return task_class, observation


class OtelBaselineFeed:
    """Subscriber that converts OTEL spans into BaselineRegistry updates.

    Wires an extractor (default: ``default_span_extractor``) to a
    ``BaselineRegistry`` instance. Calling ``ingest_span(span)`` updates
    the registry; ``ingest_batch`` walks an iterable.

    Counters track the running totals so callers can monitor health.
    """

    def __init__(
        self,
        registry: BaselineRegistry,
        *,
        span_to_observation: SpanExtractor = default_span_extractor,
    ) -> None:
        self._registry = registry
        self._extract = span_to_observation
        self.spans_seen = 0
        self.spans_accepted = 0
        self.spans_skipped = 0
        self.spans_errored = 0

    @property
    def registry(self) -> BaselineRegistry:
        return self._registry

    def ingest_span(self, span: dict[str, Any]) -> bool:
        """Update the registry from a single span. Returns True on accept."""
        self.spans_seen += 1
        if not isinstance(span, dict):
            self.spans_skipped += 1
            return False
        try:
            extracted = self._extract(span)
        except (KeyError, TypeError, ValueError) as exc:
            # guardian: allow-broad-extractor-failure -- live feed must not
            # crash on a malformed span; log and drop instead.
            logger.warning("otel_feed: extractor raised on span: %s", exc)
            self.spans_errored += 1
            return False
        if extracted is None:
            self.spans_skipped += 1
            return False
        task_class, observation = extracted
        try:
            self._registry.update(task_class, observation)
        except (OSError, ValueError) as exc:
            logger.warning("otel_feed: registry.update failed for %s: %s", task_class, exc)
            self.spans_errored += 1
            return False
        self.spans_accepted += 1
        return True

    def ingest_batch(self, spans: Iterable[dict[str, Any]]) -> int:
        """Ingest every span in an iterable. Returns count accepted."""
        accepted = 0
        for span in spans:
            if self.ingest_span(span):
                accepted += 1
        return accepted

    def stats(self) -> dict[str, int]:
        """Snapshot of running counters."""
        return {
            "spans_seen": self.spans_seen,
            "spans_accepted": self.spans_accepted,
            "spans_skipped": self.spans_skipped,
            "spans_errored": self.spans_errored,
        }


def consume_span_stream(
    feed: OtelBaselineFeed,
    stream: Iterable[dict[str, Any]],
    *,
    max_spans: int | None = None,
) -> dict[str, int]:
    """Pump a span stream into the feed. Returns final stats.

    ``max_spans`` caps total ingestion (useful for tests and bounded jobs).
    """
    count = 0
    for span in stream:
        feed.ingest_span(span)
        count += 1
        if max_spans is not None and count >= max_spans:
            break
    return feed.stats()


__all__ = [
    "OtelBaselineFeed",
    "SpanExtractor",
    "consume_span_stream",
    "default_span_extractor",
]
