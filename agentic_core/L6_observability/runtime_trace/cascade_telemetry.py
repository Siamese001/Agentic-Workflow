"""Cascade telemetry consumer for Wave 1/3 routing decisions.

Closes G7 from ``.windsurf/plans/qwen-confidence-routing-hardening-d4e7b1.md``.

The W1 ``HealingRouter._dispatch_qwen`` and W3 ``ConfidenceAwareExecutor``
stamp every dispatch result with ``tier_attempted``, ``tier_used``, and
``fallback_reason``. This module is the consumer side: an in-process
event recorder that lets ops/calibration tooling answer:

  - How often is MEDIUM demoted to LOW (vLLM unhealthy)?
  - Which fallback_reasons dominate (health-probe vs dispatch-error)?
  - Per-app cascade rate for routing-quality calibration.

The recorder is process-local and bounded (default 1024 events). It is
intentionally NOT a substitute for OTEL spans — it is a fast, dependency-
free aggregate suitable for unit tests, dashboards, and the Wave-4 CLI
audit (``tools/analysis/cascade_telemetry_report.py``, see plan W4).

Layer purity: L6 observability — never reads from L0/L4, never mutates
runtime state. Pure aggregator.
"""

from __future__ import annotations

import threading
from collections import Counter
from dataclasses import dataclass, field
from time import time
from typing import Any

# Default cap — generous enough for an hour of dense traffic on the
# 32B-AWQ server (which serves ~10 req/min sustained), small enough to
# bound memory in long-running test sessions.
DEFAULT_MAX_EVENTS: int = 1024


@dataclass(frozen=True)
class CascadeEvent:
    """A single dispatch outcome — the unit the recorder ingests."""

    app_name: str
    tier_attempted: str
    tier_used: str
    fallback_reason: str
    success: bool
    timestamp: float = field(default_factory=time)


@dataclass
class CascadeStats:
    """Aggregated view of the recorder buffer."""

    total: int
    successes: int
    failures: int
    cascades: int  # tier_attempted != tier_used
    by_fallback_reason: dict[str, int]
    by_app: dict[str, int]
    cascade_rate: float


class CascadeTelemetryRecorder:
    """Thread-safe ring buffer for cascade dispatch events.

    Use ``record_dispatch(result, app_name)`` from any caller that has the
    raw result dict from ``HealingRouter._dispatch_qwen`` /
    ``_fallback_qwen_to_flash`` or from a ``ConfidenceAwareExecutor``
    ``ExecutionResult``. The recorder is permissive — missing fields are
    treated as empty strings, never as exceptions, so wiring this in is
    always fail-open.
    """

    def __init__(self, max_events: int = DEFAULT_MAX_EVENTS) -> None:
        if max_events <= 0:
            raise ValueError(f"max_events must be > 0, got {max_events!r}")
        self._max_events = max_events
        self._events: list[CascadeEvent] = []
        self._lock = threading.Lock()

    @property
    def max_events(self) -> int:
        return self._max_events

    @property
    def event_count(self) -> int:
        with self._lock:
            return len(self._events)

    def record(self, event: CascadeEvent) -> None:
        with self._lock:
            self._events.append(event)
            overflow = len(self._events) - self._max_events
            if overflow > 0:
                # Drop oldest events first — preserve recent ones for
                # post-incident calibration.
                del self._events[:overflow]

    def record_dispatch(
        self,
        result: dict[str, Any] | Any,
        app_name: str = "unknown",
    ) -> CascadeEvent:
        """Convert a dispatch result into a ``CascadeEvent`` and store it.

        Accepts either a raw ``dict`` (from ``HealingRouter._dispatch_*``)
        or any object with attribute-style ``tier_attempted`` /
        ``tier_used`` / ``fallback_reason`` / ``success`` (e.g. a W3
        ``ExecutionResult``). Returns the event for chained inspection.
        """
        getter = (
            (lambda key, default="": result.get(key, default))
            if isinstance(result, dict)
            else (lambda key, default="": getattr(result, key, default))
        )
        event = CascadeEvent(
            app_name=app_name,
            tier_attempted=str(getter("tier_attempted", "") or ""),
            tier_used=str(getter("tier_used", "") or ""),
            fallback_reason=str(getter("fallback_reason", "") or ""),
            success=bool(getter("success", False) or False),
        )
        self.record(event)
        return event

    def snapshot(self) -> list[CascadeEvent]:
        """Return a copy of the current events buffer (immutable view)."""
        with self._lock:
            return list(self._events)

    def stats(self) -> CascadeStats:
        """Compute aggregate stats over the current buffer."""
        with self._lock:
            events = list(self._events)

        total = len(events)
        if total == 0:
            return CascadeStats(
                total=0,
                successes=0,
                failures=0,
                cascades=0,
                by_fallback_reason={},
                by_app={},
                cascade_rate=0.0,
            )

        successes = sum(1 for e in events if e.success)
        cascades = sum(
            1 for e in events if e.tier_attempted and e.tier_used and e.tier_attempted != e.tier_used
        )
        reasons = Counter(e.fallback_reason for e in events if e.fallback_reason)
        apps = Counter(e.app_name for e in events)

        return CascadeStats(
            total=total,
            successes=successes,
            failures=total - successes,
            cascades=cascades,
            by_fallback_reason=dict(reasons),
            by_app=dict(apps),
            cascade_rate=cascades / total,
        )

    def reset(self) -> None:
        with self._lock:
            self._events.clear()


# Process-wide singleton — most callers want one recorder per process.
_RECORDER_SINGLETON: dict[str, CascadeTelemetryRecorder] = {}


def get_recorder() -> CascadeTelemetryRecorder:
    inst = _RECORDER_SINGLETON.get("instance")
    if inst is None:
        inst = CascadeTelemetryRecorder()
        _RECORDER_SINGLETON["instance"] = inst
    return inst


def reset_for_tests() -> None:
    """Drop the shared recorder so tests start with an empty buffer."""
    _RECORDER_SINGLETON.clear()


__all__ = [
    "DEFAULT_MAX_EVENTS",
    "CascadeEvent",
    "CascadeStats",
    "CascadeTelemetryRecorder",
    "get_recorder",
    "reset_for_tests",
]
