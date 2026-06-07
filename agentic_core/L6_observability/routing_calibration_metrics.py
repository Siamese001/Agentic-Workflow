"""W4.P1 — OTEL metric emitters for L0 routing calibration.

Plan: ``docs/archive/windsurf/legacy-tree/plans/l0-routing-calibration-gap-audit-b3c9d4.md`` §W4.P1.

Thin, fail-soft metric-emission surface for the four key calibration
events each L0 decision produces:

* ``r1_exact_hit`` / ``r1_semantic_hit``  — cache-hit telemetry consumed
  by the W4.P2 calibration-refresh job (rolling hit-rate).
* ``r5_fired``                            — abstain decisions, counted by
  ``primary_reason`` so multi-signal R5 telemetry attributes to the
  correct trigger.
* ``r3_coverage_below_floor``              — C0 ``coverage_score <
  c0_coverage_floor`` events (the R3 gate's §C0.6 broaden-loop signal).

Design:

1. **Fail-soft.** If OTEL is not available, or any metric emission
   raises, we silently record into an in-process fallback counter. The
   ``record_count`` property exposes the counters so tests can assert
   emission without booting OTEL.
2. **Additive.** No existing OTEL pipeline is modified. The emitters are
   stand-alone; callers opt in. W4.P2's refresh job reads the fallback
   counters when OTEL is offline.
3. **Namespace dimension.** Every counter is labeled with ``namespace``
   (cache / agent class) so downstream dashboards can slice calibration
   health per agent surface without cardinality explosion.
"""

from __future__ import annotations

import logging
import threading
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

Logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Metric names — closed vocabulary for downstream dashboard stability.
# -----------------------------------------------------------------------------
METRIC_R1_EXACT_HIT = "routing.r1a.exact_hit"
METRIC_R1_SEMANTIC_HIT = "routing.r1b.semantic_hit"
METRIC_R5_FIRED = "routing.r5.fired"
METRIC_R3_COVERAGE_BELOW_FLOOR = "routing.r3.coverage_below_floor"
METRIC_R3_GROUNDED = "routing.r3.grounded"


_KNOWN_METRICS: frozenset[str] = frozenset(
    {
        METRIC_R1_EXACT_HIT,
        METRIC_R1_SEMANTIC_HIT,
        METRIC_R5_FIRED,
        METRIC_R3_COVERAGE_BELOW_FLOOR,
        METRIC_R3_GROUNDED,
    },
)


@dataclass
class _FallbackState:
    """In-process counter store used when OTEL is unavailable.

    Keys are ``(metric_name, namespace, reason_code)`` tuples. Reason
    code is empty string for metrics that don't attribute to a trigger.
    """

    counters: Counter[tuple[str, str, str]] = field(default_factory=Counter)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def incr(self, metric: str, namespace: str, reason_code: str, by: int = 1) -> None:
        with self._lock:
            self.counters[(metric, namespace, reason_code)] += by

    def snapshot(self) -> dict[tuple[str, str, str], int]:
        """Return a thread-safe copy of the counter state."""
        with self._lock:
            return dict(self.counters)

    def reset(self) -> None:
        with self._lock:
            self.counters.clear()


_STATE = _FallbackState()


def _emit_otel_counter(
    metric: str,
    *,
    namespace: str,
    reason_code: str,
    increment: int,
) -> bool:
    """Try to emit via OTEL. Returns True on success, False otherwise.

    Uses a lazy import so this module is cheap to load in environments
    without OTEL (tests, CI).
    """
    try:
        from opentelemetry import metrics as otel_metrics  # noqa: PLC0415
    except ImportError:
        return False
    try:
        meter = otel_metrics.get_meter("agentic_core.L6_observability.routing_calibration")
        counter = meter.create_counter(
            name=metric,
            description=f"L0 routing calibration counter: {metric}",
            unit="1",
        )
        attributes: dict[str, Any] = {"namespace": namespace or "default"}
        if reason_code:
            attributes["reason_code"] = reason_code
        counter.add(increment, attributes=attributes)
        return True
    except (
        AttributeError,
        TypeError,
        RuntimeError,
    ) as exc:  # guardian: allow-log-and-swallow -- OTEL emission is best-effort; fallback counter preserves signal
        Logger.debug(
            "routing_calibration_metrics: OTEL emission for %s failed: %s",
            metric,
            exc,
        )
        return False


def record_r1_exact_hit(namespace: str = "default", *, increment: int = 1) -> None:
    """Record a D1 exact-cache hit."""
    _record(METRIC_R1_EXACT_HIT, namespace=namespace, reason_code="", increment=increment)


def record_r1_semantic_hit(namespace: str = "default", *, increment: int = 1) -> None:
    """Record a D2 semantic-cache hit."""
    _record(METRIC_R1_SEMANTIC_HIT, namespace=namespace, reason_code="", increment=increment)


def record_r5_fired(
    reason_code: str,
    *,
    namespace: str = "default",
    increment: int = 1,
) -> None:
    """Record an R5 abstain, labeled by primary reason code."""
    _record(METRIC_R5_FIRED, namespace=namespace, reason_code=reason_code, increment=increment)


def record_r3_coverage_below_floor(namespace: str = "default", *, increment: int = 1) -> None:
    """Record a C0 coverage-below-floor event (R3 broaden-loop trigger)."""
    _record(
        METRIC_R3_COVERAGE_BELOW_FLOOR,
        namespace=namespace,
        reason_code="",
        increment=increment,
    )


def record_r3_grounded(namespace: str = "default", *, increment: int = 1) -> None:
    """Record a successful R3 grounded-read dispatch."""
    _record(METRIC_R3_GROUNDED, namespace=namespace, reason_code="", increment=increment)


def _record(
    metric: str,
    *,
    namespace: str,
    reason_code: str,
    increment: int,
) -> None:
    if metric not in _KNOWN_METRICS:
        Logger.warning(
            "routing_calibration_metrics: unknown metric %r; ignoring",
            metric,
        )
        return
    if increment <= 0:
        return
    # Always update the fallback counter — it's the source of truth for
    # tests and for the W4.P2 refresh job when OTEL is offline.
    _STATE.incr(metric, namespace, reason_code, by=increment)
    _emit_otel_counter(
        metric,
        namespace=namespace,
        reason_code=reason_code,
        increment=increment,
    )


def snapshot_counters() -> dict[tuple[str, str, str], int]:
    """Return a snapshot of the in-process counter state."""
    return _STATE.snapshot()


def reset_counters() -> None:
    """Reset the in-process counter state (test helper)."""
    _STATE.reset()


def hit_ratio(namespace: str = "default") -> float:
    """Compute R1 hit ratio = (r1a + r1b) / (r1a + r1b + r5_fired) for ``namespace``.

    Returns 0.0 when no events have been recorded for the namespace.
    This is the OpenAI Prompt-Caching-201 §3.1 metric analog — target
    >= 0.4 once prefix stability is established.
    """
    snap = snapshot_counters()
    r1a = snap.get((METRIC_R1_EXACT_HIT, namespace, ""), 0)
    r1b = snap.get((METRIC_R1_SEMANTIC_HIT, namespace, ""), 0)
    r5 = sum(v for (m, ns, _r), v in snap.items() if m == METRIC_R5_FIRED and ns == namespace)
    total = r1a + r1b + r5
    if total == 0:
        return 0.0
    return (r1a + r1b) / total


__all__ = [
    "METRIC_R1_EXACT_HIT",
    "METRIC_R1_SEMANTIC_HIT",
    "METRIC_R3_COVERAGE_BELOW_FLOOR",
    "METRIC_R3_GROUNDED",
    "METRIC_R5_FIRED",
    "hit_ratio",
    "record_r1_exact_hit",
    "record_r1_semantic_hit",
    "record_r3_coverage_below_floor",
    "record_r3_grounded",
    "record_r5_fired",
    "reset_counters",
    "snapshot_counters",
]
