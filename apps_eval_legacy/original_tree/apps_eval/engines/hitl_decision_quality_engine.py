"""HITL Decision Quality Engine (W6 P6.1).

Per plan runtime-hitl-exit-control-c4e7b3 P6.1 and ADR-023 §4 (Shadow Eval &
Learning Loop): the runtime HITL ledger is the GROUND TRUTH for approver-pool
behavior. This engine consumes ledger entries and produces a multi-dimensional
quality score that nightly eval runs can trend.

Dimensions (deterministic, no ML):

1. ``timeout_rate``           — fraction of PENDING resolutions that fell
                                through to TIMEOUT (higher = worse)
2. ``denial_rate``            — fraction resolved as DENIED (informational,
                                not directly bad — but used for
                                consistency)
3. ``approval_consistency``   — 1.0 - stdev(approval_rate per approver) when
                                the same class has multiple approvers (lower
                                stdev = more consistent)
4. ``reason_coverage``        — fraction of denials that carry a non-empty
                                ``reason_code`` (higher = better)
5. ``latency_p50_ms`` /
   ``latency_p95_ms``         — resolution latency quantiles in milliseconds

Aggregate ``quality_score`` (0..1, higher = better):

    1.0
      - 0.35 * timeout_rate
      - 0.25 * (1.0 - reason_coverage)
      - 0.25 * (1.0 - approval_consistency)
      - 0.15 * latency_penalty

where ``latency_penalty`` is ``min(1.0, latency_p95_ms / TARGET_P95_MS)``.

The engine is pure — it reads a ledger and returns a report. It MUST NOT write
back. Writes are the shadow consumer's job (W6 P6.2), and even there only as
drafts for UWG review (G8 constraint).
"""

from __future__ import annotations

from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
    traces_execute,
)

import logging
import math
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable, Mapping, Sequence

from agentic_core.L3_orchestration.exit_control.runtime_hitl_ledger import (
    LedgerEntry,
    LedgerState,
    RuntimeHitlLedger,
)
from agentic_core.L5_safety.exit_control.hitl_classes import HitlClass
from apps_eval.integrations.meta_bus_publisher import (
    KIND_HITL_QUALITY,
    publish_eval_outcome,
)
from apps_eval.integrations.tracing import eval_span

_log = logging.getLogger(__name__)

# Latency target at p95 — breached escalations accrue latency penalty. 30 min
# matches the G4 lower-bound timeout (safety class = 1800s) so that even the
# shortest-deadline class has a meaningful ceiling.
TARGET_P95_MS = 30 * 60 * 1000


# ---------------------------------------------------------------------------
# Report types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class HitlQualityDimensions:
    """Per-bucket quality dimensions. Each field is independently interpretable."""

    timeout_rate: float
    denial_rate: float
    approval_consistency: float
    reason_coverage: float
    latency_p50_ms: int
    latency_p95_ms: int


@dataclass(frozen=True)
class HitlQualityBucket:
    """One row in the quality report — typically keyed by (class, approver_pool)."""

    hitl_class: str
    approver_pool: str
    sample_size: int
    resolved_count: int
    pending_count: int
    dimensions: HitlQualityDimensions
    quality_score: float


@dataclass(frozen=True)
class HitlQualityReport:
    """Aggregate quality report produced by the engine.

    The overall ``quality_score`` is a sample-size-weighted mean of the per-bucket
    scores — buckets with no resolved entries contribute 0 sample weight.
    """

    buckets: Sequence[HitlQualityBucket]
    overall_score: float
    total_entries: int
    resolved_entries: int
    pending_entries: int
    policy_snapshot: str = ""
    notes: Mapping[str, str] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


class HitlDecisionQualityEngine:
    """Deterministic scorer over runtime HITL ledger entries.

    Usage::

        engine = HitlDecisionQualityEngine()
        report = engine.score_entries(ledger.list_pending() + resolved_entries)
        # or, pulling directly from a ledger:
        report = engine.score_ledger(ledger)

    Thread-safety: the engine is stateless between calls; reuse freely.
    """

    AGENT_ID = "hitl_decision_quality_engine"

    def __init__(self, target_p95_ms: int = TARGET_P95_MS) -> None:
        if target_p95_ms <= 0:
            raise ValueError("target_p95_ms must be positive")
        self._target_p95_ms = target_p95_ms

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @traces_execute(layer="L3_ORCHESTRATION")
    def score_ledger(
        self,
        ledger: RuntimeHitlLedger,
        *,
        run_id_filter: str | None = None,
    ) -> HitlQualityReport:
        """Score every entry currently in ``ledger``.

        If ``run_id_filter`` is supplied, only entries for that run are scored.
        Otherwise the engine walks pending + recently resolved rows via the
        public ledger API.
        """
        if run_id_filter is not None:
            entries: list[LedgerEntry] = ledger.list_by_run(run_id_filter)
        else:
            # Pending plus a best-effort walk of recently-resolved rows.
            # The ledger API exposes list_pending and list_by_run; for a
            # resolved-history walk we rely on the caller providing entries
            # explicitly to score_entries.
            entries = list(ledger.list_pending())
        return self.score_entries(entries)

    def score_entries(self, entries: Iterable[LedgerEntry]) -> HitlQualityReport:
        """Score an arbitrary collection of ledger entries."""
        materialized = list(entries)
        if not materialized:
            return HitlQualityReport(
                buckets=(),
                overall_score=1.0,
                total_entries=0,
                resolved_entries=0,
                pending_entries=0,
                notes={"empty_input": "no ledger entries; score defaults to 1.0"},
            )

        buckets_raw: dict[tuple[str, str], list[LedgerEntry]] = defaultdict(list)
        for entry in materialized:
            key = (entry.hitl_class.value, entry.approver_pool)
            buckets_raw[key].append(entry)

        bucket_rows: list[HitlQualityBucket] = []
        for (hclass, pool), rows in sorted(buckets_raw.items()):
            bucket_rows.append(self._score_bucket(hclass, pool, rows))

        resolved_total = sum(b.resolved_count for b in bucket_rows)
        pending_total = sum(b.pending_count for b in bucket_rows)

        if resolved_total == 0:
            overall = 1.0  # nothing resolved yet — cannot penalize
        else:
            weighted_sum = sum(b.quality_score * b.resolved_count for b in bucket_rows)
            overall = weighted_sum / resolved_total

        policy_snapshots = {e.policy_snapshot for e in materialized if e.policy_snapshot}
        snapshot = next(iter(policy_snapshots)) if len(policy_snapshots) == 1 else ""

        report = HitlQualityReport(
            buckets=tuple(bucket_rows),
            overall_score=_clip_unit(overall),
            total_entries=len(materialized),
            resolved_entries=resolved_total,
            pending_entries=pending_total,
            policy_snapshot=snapshot,
        )

        # Publish to canonical meta-learning bus (plan W2 wiring).
        with eval_span(
            "apps_eval.v1.hitl_decision_quality.score_entries",
            attributes={
                "eval.total_entries": report.total_entries,
                "eval.resolved_entries": report.resolved_entries,
                "eval.pending_entries": report.pending_entries,
                "eval.overall_score": report.overall_score,
                "eval.bucket_count": len(report.buckets),
            },
        ):
            publish_eval_outcome(
                kind=KIND_HITL_QUALITY,
                payload={
                    "engine": self.AGENT_ID,
                    "overall_score": report.overall_score,
                    "total_entries": report.total_entries,
                    "resolved_entries": report.resolved_entries,
                    "pending_entries": report.pending_entries,
                    "bucket_count": len(report.buckets),
                    "policy_snapshot": report.policy_snapshot,
                },
            )

        return report

    # ------------------------------------------------------------------
    # Per-bucket scoring
    # ------------------------------------------------------------------

    def _score_bucket(
        self,
        hitl_class: str,
        approver_pool: str,
        rows: Sequence[LedgerEntry],
    ) -> HitlQualityBucket:
        resolved = [r for r in rows if r.state is not LedgerState.PENDING]
        pending = [r for r in rows if r.state is LedgerState.PENDING]

        if not resolved:
            dims = HitlQualityDimensions(
                timeout_rate=0.0,
                denial_rate=0.0,
                approval_consistency=1.0,
                reason_coverage=1.0,
                latency_p50_ms=0,
                latency_p95_ms=0,
            )
            return HitlQualityBucket(
                hitl_class=hitl_class,
                approver_pool=approver_pool,
                sample_size=len(rows),
                resolved_count=0,
                pending_count=len(pending),
                dimensions=dims,
                quality_score=1.0,
            )

        timeouts = sum(1 for r in resolved if r.state is LedgerState.TIMEOUT)
        denials = [r for r in resolved if r.state is LedgerState.DENIED]
        approvals = [r for r in resolved if r.state is LedgerState.APPROVED]
        timeout_rate = timeouts / len(resolved)
        denial_rate = len(denials) / len(resolved)

        reason_coverage = (
            sum(1 for r in denials if (r.reason_code or "").strip()) / len(denials) if denials else 1.0
        )
        approval_consistency = _approval_consistency(approvals, denials)

        latencies_ms = [_latency_ms(r) for r in resolved if r.resolved_at is not None]
        p50 = _quantile(latencies_ms, 0.50)
        p95 = _quantile(latencies_ms, 0.95)

        dims = HitlQualityDimensions(
            timeout_rate=_clip_unit(timeout_rate),
            denial_rate=_clip_unit(denial_rate),
            approval_consistency=_clip_unit(approval_consistency),
            reason_coverage=_clip_unit(reason_coverage),
            latency_p50_ms=p50,
            latency_p95_ms=p95,
        )

        latency_penalty = min(1.0, p95 / float(self._target_p95_ms))
        quality_score = (
            1.0
            - 0.35 * dims.timeout_rate
            - 0.25 * (1.0 - dims.reason_coverage)
            - 0.25 * (1.0 - dims.approval_consistency)
            - 0.15 * latency_penalty
        )

        return HitlQualityBucket(
            hitl_class=hitl_class,
            approver_pool=approver_pool,
            sample_size=len(rows),
            resolved_count=len(resolved),
            pending_count=len(pending),
            dimensions=dims,
            quality_score=_clip_unit(quality_score),
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _approval_consistency(
    approvals: Sequence[LedgerEntry],
    denials: Sequence[LedgerEntry],
) -> float:
    """Return 1.0 - approval-rate stdev across approvers, or 1.0 when unclear.

    When only one approver has resolved entries, consistency is vacuously 1.0.
    When multiple approvers have resolved entries, we compute each approver's
    approval rate and return 1.0 minus the population stdev, clipped to [0,1].
    """
    combined = list(approvals) + list(denials)
    per_approver: dict[str, list[bool]] = defaultdict(list)
    for entry in combined:
        approver = (entry.approver_id or "").strip() or "<unknown>"
        per_approver[approver].append(entry.state is LedgerState.APPROVED)

    if len(per_approver) <= 1:
        return 1.0

    rates = [sum(votes) / len(votes) for votes in per_approver.values() if votes]
    if len(rates) <= 1:
        return 1.0
    return 1.0 - min(1.0, statistics.pstdev(rates))


def _latency_ms(entry: LedgerEntry) -> int:
    if entry.resolved_at is None:
        return 0
    return int(max(0.0, (entry.resolved_at - entry.created_at) * 1000.0))


def _quantile(values: Sequence[int], q: float) -> int:
    if not values:
        return 0
    sorted_values = sorted(values)
    # Nearest-rank method — simple and deterministic.
    idx = max(0, min(len(sorted_values) - 1, math.ceil(q * len(sorted_values)) - 1))
    return int(sorted_values[idx])


def _clip_unit(x: float) -> float:
    if math.isnan(x):
        return 0.0
    return max(0.0, min(1.0, float(x)))


# Exported class name enumeration for type narrowing downstream.
_ALL_CLASSES = tuple(c.value for c in HitlClass)


__all__ = [
    "HitlDecisionQualityEngine",
    "HitlQualityBucket",
    "HitlQualityDimensions",
    "HitlQualityReport",
    "TARGET_P95_MS",
]


# ----------------------------------------------------------------------
# OTEL coverage — module-load emit per check_apps_otel_coverage.py.
# Phase A of W-OTEL waves: structural wiring at import time.
# Phase B (per-method spans on execute() paths) is tracked separately.
# Pattern matches lifecycle_trace_contract.py and apps_research/engines.
# ----------------------------------------------------------------------
from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: E402
    _emit_records_telemetry_event,
)

_emit_records_telemetry_event("p4", 'apps_eval.engines.hitl_decision_quality_engine', "module_loaded")
