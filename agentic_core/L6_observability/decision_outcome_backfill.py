"""Outcome backfill API for the unified ``decision_events`` table.

Plan: ``docs/archive/windsurf/legacy-tree/plans/routing-decision-process-enhancement-9c7e4d.md`` Wave W2.

GAP-2: ``outcome_success`` is currently nullable. In practice ~all rows are NULL
because nothing forces Exit Eval to populate it after sealing. This starves the
meta-learner replay buffer, the Brier calibrator, and every auto-rollback path.

This module provides the canonical API:

* ``backfill_outcome(conn, decision_id, outcome_success, latency_ms_total=...)``
  — idempotent populate.
* ``BackfillLagSummary`` — observability aggregate over recent backfills.
* ``record_backfill_lag(seconds)`` — fail-soft OTEL histogram emission.

Design:

1. **Idempotent.** Re-calling ``backfill_outcome`` with the same
   ``(decision_id, outcome_success, error_code)`` triple is a no-op; with a
   conflicting outcome it raises :class:`OutcomeBackfillConflictError`.
2. **Strict on missing rows.** Backfilling a non-existent ``decision_id`` raises
   :class:`DecisionRowMissingError`. Callers MUST insert the decision row
   before sealing, never after.
3. **Lag instrumentation.** Every backfill emits ``decision.outcome.backfill_lag``
   with bucketed seconds since the original decision timestamp. Lag > target
   SLO is the primary signal that Exit Eval is leaking outcomes.

The module deliberately depends on no MCP / OTEL surface at import time —
``record_backfill_lag`` lazy-imports OTEL and falls back to the in-process
fallback counter shared with ``routing_calibration_metrics``.
"""

from __future__ import annotations

import logging
import sqlite3
import threading
import time
from dataclasses import dataclass, field
from typing import Any

Logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Errors.
# ---------------------------------------------------------------------------


class DecisionRowMissingError(LookupError):
    """``backfill_outcome`` called on a ``decision_id`` that does not exist."""


class OutcomeBackfillConflictError(ValueError):
    """``backfill_outcome`` called with a different outcome than already stored."""


# ---------------------------------------------------------------------------
# Lag instrumentation — fail-soft OTEL + in-process fallback.
# ---------------------------------------------------------------------------

METRIC_BACKFILL_LAG: str = "routing.decision.outcome.backfill_lag_seconds"

# Bucket boundaries (seconds) — coarse enough to read in a dashboard
# without cardinality blow-up.
LAG_BUCKETS_SECONDS: tuple[float, ...] = (1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 1800.0)


@dataclass
class _LagState:
    """In-process fallback histogram for ``METRIC_BACKFILL_LAG``."""

    bucket_counts: dict[float, int] = field(
        default_factory=lambda: {b: 0 for b in LAG_BUCKETS_SECONDS},
    )
    overflow_count: int = 0
    sum_seconds: float = 0.0
    sample_count: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def observe(self, seconds: float) -> None:
        with self._lock:
            self.sample_count += 1
            self.sum_seconds += seconds
            placed = False
            for boundary in LAG_BUCKETS_SECONDS:
                if seconds <= boundary:
                    self.bucket_counts[boundary] += 1
                    placed = True
                    break
            if not placed:
                self.overflow_count += 1

    def reset(self) -> None:
        with self._lock:
            self.bucket_counts = {b: 0 for b in LAG_BUCKETS_SECONDS}
            self.overflow_count = 0
            self.sum_seconds = 0.0
            self.sample_count = 0


_LAG_STATE = _LagState()


def _emit_otel_lag(seconds: float) -> bool:
    """Try to record the lag observation via OTEL. Returns True on success."""
    try:
        from opentelemetry import metrics as otel_metrics  # noqa: PLC0415
    except ImportError:
        return False
    try:
        meter = otel_metrics.get_meter("agentic_core.L6_observability.decision_outcome_backfill")
        hist = meter.create_histogram(
            name=METRIC_BACKFILL_LAG,
            description="Seconds elapsed between decision and outcome backfill",
            unit="s",
        )
        hist.record(seconds)
        return True
    except (
        AttributeError,
        TypeError,
        RuntimeError,
    ) as exc:  # guardian: allow-log-and-swallow -- OTEL emission best-effort; fallback histogram preserves signal
        Logger.debug("decision_outcome_backfill: OTEL lag emission failed: %s", exc)
        return False


def record_backfill_lag(seconds: float) -> None:
    """Record one backfill-lag observation (fail-soft).

    Always updates the in-process fallback. Best-effort OTEL emission on top.
    """
    if seconds < 0:
        seconds = 0.0
    _LAG_STATE.observe(seconds)
    _emit_otel_lag(seconds)


@dataclass
class BackfillLagSummary:
    """Snapshot of the in-process backfill-lag histogram."""

    sample_count: int
    sum_seconds: float
    bucket_counts: dict[float, int]
    overflow_count: int

    @property
    def mean_seconds(self) -> float:
        if self.sample_count == 0:
            return 0.0
        return self.sum_seconds / self.sample_count


def lag_summary() -> BackfillLagSummary:
    """Return a thread-safe snapshot of the in-process histogram."""
    with _LAG_STATE._lock:  # noqa: SLF001
        return BackfillLagSummary(
            sample_count=_LAG_STATE.sample_count,
            sum_seconds=_LAG_STATE.sum_seconds,
            bucket_counts=dict(_LAG_STATE.bucket_counts),
            overflow_count=_LAG_STATE.overflow_count,
        )


def reset_lag_state() -> None:
    """Reset in-process state — test-only helper."""
    _LAG_STATE.reset()


# ---------------------------------------------------------------------------
# Backfill API.
# ---------------------------------------------------------------------------


def backfill_outcome(
    conn: sqlite3.Connection,
    decision_id: str,
    outcome_success: bool,
    *,
    latency_ms_total: int | None = None,
    error_code: str | None = None,
    now: float | None = None,
) -> dict[str, Any]:
    """Populate ``outcome_success`` (and optional ``latency_ms`` / ``error_code``).

    Args:
        conn: Open SQLite connection. Caller owns lifetime.
        decision_id: PK of the row to update. Must already exist.
        outcome_success: Final disposition from Exit Eval.
        latency_ms_total: Optional end-to-end latency. Updates ``latency_ms``
            only when the existing value is NULL — never overwrites.
        error_code: Optional error code (only set when ``outcome_success=False``).
        now: Override clock for tests. Default ``time.time()``.

    Returns:
        ``{"updated": bool, "lag_seconds": float, "no_op": bool}`` — ``no_op``
        is True when the row already had the same outcome (idempotent path).

    Raises:
        DecisionRowMissingError: ``decision_id`` is not in ``decision_events``.
        OutcomeBackfillConflictError: Row already has a non-null
            ``outcome_success`` that contradicts the requested value.
    """
    if now is None:
        now = time.time()
    cur = conn.cursor()
    row = cur.execute(
        "SELECT timestamp, outcome_success, latency_ms, error_code "
        "FROM decision_events WHERE decision_id = ?",
        (decision_id,),
    ).fetchone()
    if row is None:
        raise DecisionRowMissingError(
            f"decision_id={decision_id!r} not found in decision_events; "
            "insert the decision row before backfilling outcome",
        )
    decision_ts, existing_outcome, existing_latency, existing_error = row
    requested_int = 1 if outcome_success else 0
    # Conflict check
    if existing_outcome is not None and existing_outcome != requested_int:
        raise OutcomeBackfillConflictError(
            f"decision_id={decision_id!r} already has "
            f"outcome_success={bool(existing_outcome)}; refusing to overwrite "
            f"with {outcome_success}",
        )
    # Idempotent no-op path
    if (
        existing_outcome == requested_int
        and (latency_ms_total is None or existing_latency is not None)
        and (error_code is None or existing_error == error_code)
    ):
        return {"updated": False, "lag_seconds": 0.0, "no_op": True}
    # Resolve final values — never overwrite an existing latency or error_code
    final_latency = existing_latency if existing_latency is not None else latency_ms_total
    final_error = existing_error if existing_error is not None else error_code
    cur.execute(
        """
        UPDATE decision_events
           SET outcome_success     = ?,
               outcome_backfill_ts = ?,
               latency_ms          = ?,
               error_code          = ?
         WHERE decision_id = ?
        """,
        (
            requested_int,
            now,
            final_latency,
            final_error,
            decision_id,
        ),
    )
    conn.commit()
    lag_seconds = max(0.0, now - float(decision_ts))
    record_backfill_lag(lag_seconds)
    return {"updated": True, "lag_seconds": lag_seconds, "no_op": False}


__all__ = [
    "BackfillLagSummary",
    "DecisionRowMissingError",
    "LAG_BUCKETS_SECONDS",
    "METRIC_BACKFILL_LAG",
    "OutcomeBackfillConflictError",
    "backfill_outcome",
    "lag_summary",
    "record_backfill_lag",
    "reset_lag_state",
]
