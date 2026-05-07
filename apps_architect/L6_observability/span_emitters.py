"""OTEL span emitters for apps_architect operations.

Plan: ``.windsurf/plans/apps-architect-pattern-hardening-d7e4f9.md`` W5.P1.

Emits spans for: architect.scan, architect.delta, architect.rules, architect.sync.
Fail-soft: if OTEL is unavailable, spans are silently dropped.
"""

from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from typing import Any, Iterator

_log = logging.getLogger(__name__)


def _try_get_tracer():
    try:
        from opentelemetry import trace
        return trace.get_tracer("apps_architect")
    except Exception:
        return None


class ArchitectSpanEmitter:
    """Emits OTEL spans for architect pipeline operations."""

    @contextmanager
    def span(self, name: str, attributes: dict[str, Any] | None = None) -> Iterator[Any]:
        tracer = _try_get_tracer()
        if tracer is None:
            yield None
            return
        start = time.monotonic()
        attrs = dict(attributes or {})
        span = None
        try:
            with tracer.start_as_current_span(name) as span:
                yield span
        except Exception as exc:
            attrs["error"] = str(exc)[:200]
            if span is not None:
                span.set_attribute("error", True)
                span.set_attribute("exception.message", str(exc)[:200])
            raise
        finally:
            elapsed_ms = (time.monotonic() - start) * 1000
            _log.debug("[otel] %s: %.1fms attrs=%s", name, elapsed_ms, attrs)


def emit_scan_span(pattern_count: int, scan_depth_days: int) -> None:
    emitter = ArchitectSpanEmitter()
    with emitter.span("architect.scan", {
        "pattern_count": pattern_count,
        "scan_depth_days": scan_depth_days,
    }):
        pass


def emit_delta_span(total: int, new_count: int, drift_count: int, missing_count: int) -> None:
    emitter = ArchitectSpanEmitter()
    with emitter.span("architect.delta", {
        "total_patterns": total,
        "new_count": new_count,
        "drift_count": drift_count,
        "missing_count": missing_count,
    }):
        pass


def emit_rules_span(rules_count: int, severity_filter: str = "all") -> None:
    emitter = ArchitectSpanEmitter()
    with emitter.span("architect.rules", {
        "rules_count": rules_count,
        "severity_filter": severity_filter,
    }):
        pass


def emit_sync_span(dry_run: bool, content_length: int, pr_url: str = "") -> None:
    emitter = ArchitectSpanEmitter()
    with emitter.span("architect.sync", {
        "dry_run": dry_run,
        "content_length": content_length,
        "pr_url": pr_url,
    }):
        pass


__all__ = [
    "ArchitectSpanEmitter",
    "emit_scan_span",
    "emit_delta_span",
    "emit_rules_span",
    "emit_sync_span",
]
