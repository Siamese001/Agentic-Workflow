"""Deterministic HITL decision-quality scoring for L6 consumers."""

from __future__ import annotations

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

TARGET_P95_MS = 30 * 60 * 1000


@dataclass(frozen=True)
class HitlQualityDimensions:
    timeout_rate: float
    denial_rate: float
    approval_consistency: float
    reason_coverage: float
    latency_p50_ms: int
    latency_p95_ms: int


@dataclass(frozen=True)
class HitlQualityBucket:
    hitl_class: str
    approver_pool: str
    sample_size: int
    resolved_count: int
    pending_count: int
    dimensions: HitlQualityDimensions
    quality_score: float


@dataclass(frozen=True)
class HitlQualityReport:
    buckets: Sequence[HitlQualityBucket]
    overall_score: float
    total_entries: int
    resolved_entries: int
    pending_entries: int
    policy_snapshot: str = ""
    notes: Mapping[str, str] = field(default_factory=dict)


class HitlDecisionQualityEngine:
    """Pure scorer over runtime HITL ledger entries."""

    AGENT_ID = "hitl_decision_quality_engine"

    def __init__(self, target_p95_ms: int = TARGET_P95_MS) -> None:
        if target_p95_ms <= 0:
            raise ValueError("target_p95_ms must be positive")
        self._target_p95_ms = target_p95_ms

    def score_ledger(
        self,
        ledger: RuntimeHitlLedger,
        *,
        run_id_filter: str | None = None,
    ) -> HitlQualityReport:
        if run_id_filter is not None:
            entries = ledger.list_by_run(run_id_filter)
        else:
            entries = list(ledger.list_pending())
        return self.score_entries(entries)

    def score_entries(self, entries: Iterable[LedgerEntry]) -> HitlQualityReport:
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
            buckets_raw[(entry.hitl_class.value, entry.approver_pool)].append(entry)

        buckets = tuple(
            self._score_bucket(hclass, pool, rows)
            for (hclass, pool), rows in sorted(buckets_raw.items())
        )
        resolved_total = sum(bucket.resolved_count for bucket in buckets)
        pending_total = sum(bucket.pending_count for bucket in buckets)
        overall = (
            1.0
            if resolved_total == 0
            else sum(bucket.quality_score * bucket.resolved_count for bucket in buckets)
            / resolved_total
        )
        snapshots = {entry.policy_snapshot for entry in materialized if entry.policy_snapshot}
        snapshot = next(iter(snapshots)) if len(snapshots) == 1 else ""
        return HitlQualityReport(
            buckets=buckets,
            overall_score=_clip_unit(overall),
            total_entries=len(materialized),
            resolved_entries=resolved_total,
            pending_entries=pending_total,
            policy_snapshot=snapshot,
        )

    def _score_bucket(
        self,
        hitl_class: str,
        approver_pool: str,
        rows: Sequence[LedgerEntry],
    ) -> HitlQualityBucket:
        resolved = [row for row in rows if row.state is not LedgerState.PENDING]
        pending = [row for row in rows if row.state is LedgerState.PENDING]
        if not resolved:
            return HitlQualityBucket(
                hitl_class=hitl_class,
                approver_pool=approver_pool,
                sample_size=len(rows),
                resolved_count=0,
                pending_count=len(pending),
                dimensions=HitlQualityDimensions(0.0, 0.0, 1.0, 1.0, 0, 0),
                quality_score=1.0,
            )

        timeouts = sum(1 for row in resolved if row.state is LedgerState.TIMEOUT)
        denials = [row for row in resolved if row.state is LedgerState.DENIED]
        approvals = [row for row in resolved if row.state is LedgerState.APPROVED]
        reason_coverage = (
            sum(1 for row in denials if (row.reason_code or "").strip()) / len(denials)
            if denials
            else 1.0
        )
        latencies_ms = [_latency_ms(row) for row in resolved if row.resolved_at is not None]
        p50 = _quantile(latencies_ms, 0.50)
        p95 = _quantile(latencies_ms, 0.95)
        dims = HitlQualityDimensions(
            timeout_rate=_clip_unit(timeouts / len(resolved)),
            denial_rate=_clip_unit(len(denials) / len(resolved)),
            approval_consistency=_clip_unit(_approval_consistency(approvals, denials)),
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


def _approval_consistency(
    approvals: Sequence[LedgerEntry],
    denials: Sequence[LedgerEntry],
) -> float:
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
    idx = max(0, min(len(sorted_values) - 1, math.ceil(q * len(sorted_values)) - 1))
    return int(sorted_values[idx])


def _clip_unit(x: float) -> float:
    if math.isnan(x):
        return 0.0
    return max(0.0, min(1.0, float(x)))


_ALL_CLASSES = tuple(c.value for c in HitlClass)


__all__ = [
    "HitlDecisionQualityEngine",
    "HitlQualityBucket",
    "HitlQualityDimensions",
    "HitlQualityReport",
    "TARGET_P95_MS",
]
