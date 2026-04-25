"""V6 KPI producer helpers — one pure function per KPI.

Each helper computes a KPI value from already-available inputs and records
it into the singleton :class:`V6KPIBoard`. The helpers are deliberately
free of I/O and side-effects other than writing to the board, so call
sites can adopt them with a single line without pulling in any new
dependencies.

Design invariants
-----------------
- **Single-line adoption**: every helper takes the minimum inputs a
  producer already has in scope and returns the recorded ``V6KPISample``.
- **Never raise**: a producer must never crash because KPI instrumentation
  failed. All helpers wrap the recording call in a guardian-exempted
  try/except that logs at WARNING.
- **Idempotent**: calling a helper twice with the same inputs produces the
  same recorded value (last-write-wins by design).
- **No time travel**: ``now`` defaults to :func:`time.time`; tests override
  via the explicit parameter.
"""

from __future__ import annotations

import logging
import time
from typing import Mapping

from system_learning.engines.v6_kpi_board import (
    V6KPIBoard,
    V6KPIName,
    V6KPISample,
)

logger = logging.getLogger(__name__)


def _record(
    board: V6KPIBoard,
    name: V6KPIName,
    value: float,
    *,
    source: str,
    timestamp: float | None = None,
    metadata: Mapping[str, object] | None = None,
) -> V6KPISample | None:
    """Internal helper that never raises.

    Returns the recorded sample, or ``None`` if recording failed (logged).
    """
    try:
        return board.record_value(
            name,
            float(value),
            source=source,
            timestamp=timestamp,
            metadata=metadata,
        )
    except (ValueError, TypeError, KeyError) as exc:  # guardian: allow-specific -- KPI recording must not crash producer
        logger.warning(
            "v6_kpi_producers: failed to record %s from %s: %s",
            name.value,
            source,
            exc,
        )
        return None


# --------------------------------------------------------------------------
# 6A: TRACE_INGEST_FRESHNESS — newest ingested span age in seconds
# --------------------------------------------------------------------------


def record_trace_ingest_freshness(
    board: V6KPIBoard,
    *,
    newest_span_epoch: float,
    now: float | None = None,
    source: str = "otel_runtime_ingest",
) -> V6KPISample | None:
    """Record ``now - newest_span_epoch`` as trace-ingest-freshness age."""
    ts = now if now is not None else time.time()
    age = max(0.0, ts - float(newest_span_epoch))
    return _record(
        board,
        V6KPIName.TRACE_INGEST_FRESHNESS,
        age,
        source=source,
        timestamp=ts,
        metadata={"newest_span_epoch": newest_span_epoch},
    )


# --------------------------------------------------------------------------
# 6B: EVAL_COVERAGE_OF_RUNS — runs_with_eval / total_runs in last 24h
# --------------------------------------------------------------------------


def record_eval_coverage(
    board: V6KPIBoard,
    *,
    runs_with_eval: int,
    total_runs: int,
    now: float | None = None,
    source: str = "outcome_evaluation_engine",
) -> V6KPISample | None:
    """Record eval coverage as a ratio in [0.0, 1.0]."""
    if total_runs <= 0:
        ratio = 0.0
    else:
        ratio = max(0.0, min(1.0, runs_with_eval / total_runs))
    return _record(
        board,
        V6KPIName.EVAL_COVERAGE_OF_RUNS,
        ratio,
        source=source,
        timestamp=now,
        metadata={"runs_with_eval": runs_with_eval, "total_runs": total_runs},
    )


# --------------------------------------------------------------------------
# 6B: JUDGE_UNKNOWN_BUDGET_COMPLIANCE — % judges within rubric unknown_budget
# --------------------------------------------------------------------------


def record_judge_unknown_budget_compliance(
    board: V6KPIBoard,
    *,
    compliant_judges: int,
    total_judges: int,
    now: float | None = None,
    source: str = "human_calibration_engine",
) -> V6KPISample | None:
    if total_judges <= 0:
        ratio = 0.0
    else:
        ratio = max(0.0, min(1.0, compliant_judges / total_judges))
    return _record(
        board,
        V6KPIName.JUDGE_UNKNOWN_BUDGET_COMPLIANCE,
        ratio,
        source=source,
        timestamp=now,
        metadata={
            "compliant_judges": compliant_judges,
            "total_judges": total_judges,
        },
    )


# --------------------------------------------------------------------------
# 6B/S2D: JUDGE_HUMAN_KAPPA_FRESHNESS — age in seconds since last calibration
# --------------------------------------------------------------------------


def record_judge_human_kappa_freshness(
    board: V6KPIBoard,
    *,
    last_calibration_epoch: float,
    rubric_id: str,
    now: float | None = None,
    source: str = "human_calibration_engine",
) -> V6KPISample | None:
    ts = now if now is not None else time.time()
    age = max(0.0, ts - float(last_calibration_epoch))
    return _record(
        board,
        V6KPIName.JUDGE_HUMAN_KAPPA_FRESHNESS,
        age,
        source=source,
        timestamp=ts,
        metadata={"rubric_id": rubric_id, "last_calibration_epoch": last_calibration_epoch},
    )


# --------------------------------------------------------------------------
# 6C: RCA_TO_PROPOSAL_LEAD_TIME — p95 incident-close -> proposal in seconds
# --------------------------------------------------------------------------


def record_rca_to_proposal_lead_time(
    board: V6KPIBoard,
    *,
    p95_seconds: float,
    sample_size: int,
    now: float | None = None,
    source: str = "rca_engine",
) -> V6KPISample | None:
    return _record(
        board,
        V6KPIName.RCA_TO_PROPOSAL_LEAD_TIME,
        max(0.0, float(p95_seconds)),
        source=source,
        timestamp=now,
        metadata={"sample_size": sample_size},
    )


# --------------------------------------------------------------------------
# 6D: GAUNTLET_FALSE_PROMOTE_RATE — reverted / total ratio
# --------------------------------------------------------------------------


def record_gauntlet_false_promote_rate(
    board: V6KPIBoard,
    *,
    reverted_promotions: int,
    total_promotions: int,
    now: float | None = None,
    source: str = "approval_gauntlet_engine",
) -> V6KPISample | None:
    if total_promotions <= 0:
        ratio = 0.0
    else:
        ratio = max(0.0, min(1.0, reverted_promotions / total_promotions))
    return _record(
        board,
        V6KPIName.GAUNTLET_FALSE_PROMOTE_RATE,
        ratio,
        source=source,
        timestamp=now,
        metadata={
            "reverted_promotions": reverted_promotions,
            "total_promotions": total_promotions,
        },
    )


# --------------------------------------------------------------------------
# 6D: UWG_INK_PATH_UNIQUENESS — count of non-UWG writers detected
# --------------------------------------------------------------------------


def record_uwg_ink_path_uniqueness(
    board: V6KPIBoard,
    *,
    non_uwg_writers_detected: int,
    now: float | None = None,
    source: str = "surface_isolation_validator",
) -> V6KPISample | None:
    return _record(
        board,
        V6KPIName.UWG_INK_PATH_UNIQUENESS,
        float(max(0, int(non_uwg_writers_detected))),
        source=source,
        timestamp=now,
        metadata={"raw_count": non_uwg_writers_detected},
    )


# --------------------------------------------------------------------------
# 6D: REPLAY_DIVERGENCE_LOCALIZATION — % failed replays that pinpoint a span
# --------------------------------------------------------------------------


def record_replay_divergence_localization(
    board: V6KPIBoard,
    *,
    localized_failures: int,
    total_failures: int,
    now: float | None = None,
    source: str = "deterministic_replay_engine",
) -> V6KPISample | None:
    if total_failures <= 0:
        # No failures == nothing to localize; report perfect localization by
        # convention so a quiet day does not flag red.
        ratio = 1.0
    else:
        ratio = max(0.0, min(1.0, localized_failures / total_failures))
    return _record(
        board,
        V6KPIName.REPLAY_DIVERGENCE_LOCALIZATION,
        ratio,
        source=source,
        timestamp=now,
        metadata={
            "localized_failures": localized_failures,
            "total_failures": total_failures,
        },
    )


# --------------------------------------------------------------------------
# 6D: EVAL_FRESHNESS_ON_WRITE — % writes with fresh gating eval
# --------------------------------------------------------------------------


def record_eval_freshness_on_write(
    board: V6KPIBoard,
    *,
    fresh_writes: int,
    total_writes: int,
    now: float | None = None,
    source: str = "eval_freshness_gate",
) -> V6KPISample | None:
    if total_writes <= 0:
        ratio = 1.0  # no writes == vacuously 100% fresh
    else:
        ratio = max(0.0, min(1.0, fresh_writes / total_writes))
    return _record(
        board,
        V6KPIName.EVAL_FRESHNESS_ON_WRITE,
        ratio,
        source=source,
        timestamp=now,
        metadata={"fresh_writes": fresh_writes, "total_writes": total_writes},
    )


# --------------------------------------------------------------------------
# cross: EXEMPLAR_HIT_RATE — % plans that consulted AND used an exemplar hit
# --------------------------------------------------------------------------


def record_exemplar_hit_rate(
    board: V6KPIBoard,
    *,
    plans_with_exemplar_hit: int,
    total_plans: int,
    now: float | None = None,
    source: str = "trajectory_exemplar_store",
) -> V6KPISample | None:
    if total_plans <= 0:
        ratio = 0.0
    else:
        ratio = max(0.0, min(1.0, plans_with_exemplar_hit / total_plans))
    return _record(
        board,
        V6KPIName.EXEMPLAR_HIT_RATE,
        ratio,
        source=source,
        timestamp=now,
        metadata={
            "plans_with_exemplar_hit": plans_with_exemplar_hit,
            "total_plans": total_plans,
        },
    )


# --------------------------------------------------------------------------
# 6B: SATURATION_WATCH — % capability evals static >= 30 days
# --------------------------------------------------------------------------


def record_saturation_watch(
    board: V6KPIBoard,
    *,
    static_30d_evals: int,
    total_evals: int,
    now: float | None = None,
    source: str = "shadow_drift_analyzer",
) -> V6KPISample | None:
    if total_evals <= 0:
        ratio = 0.0
    else:
        ratio = max(0.0, min(1.0, static_30d_evals / total_evals))
    return _record(
        board,
        V6KPIName.SATURATION_WATCH,
        ratio,
        source=source,
        timestamp=now,
        metadata={"static_30d_evals": static_30d_evals, "total_evals": total_evals},
    )


__all__ = [
    "record_trace_ingest_freshness",
    "record_eval_coverage",
    "record_judge_unknown_budget_compliance",
    "record_judge_human_kappa_freshness",
    "record_rca_to_proposal_lead_time",
    "record_gauntlet_false_promote_rate",
    "record_uwg_ink_path_uniqueness",
    "record_replay_divergence_localization",
    "record_eval_freshness_on_write",
    "record_exemplar_hit_rate",
    "record_saturation_watch",
]
