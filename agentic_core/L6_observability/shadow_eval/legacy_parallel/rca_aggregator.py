"""
agentic_core/L6_observability/utils/evaluation/rca_aggregator.py

RCA aggregator — clusters ShadowEvalResults into RCA-ready packets grouped by:
  - lane / route identifier
  - dominant failure mode (regression tag)
  - collection / retrieval surface
  - severity based on failure count

Future-run only.  In-memory only.  No durable writes.  No L4 access.
"""

from __future__ import annotations

import hashlib
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from agentic_core.utils.runners.providers import (
    get_clock,
)  # guardian: allow-layer-violation -- L6 observability module uses L2 execution type; intentional cross-layer instrumentation dependency

if TYPE_CHECKING:
    from agentic_core.L6_observability.shadow_eval.legacy_parallel.shadow_eval_grader import ShadowEvalResult


@dataclass
class RcaCluster:
    """RCA-ready cluster of correlated shadow-eval failures.

    Not frozen — aggregated incrementally. Not promoted yet.

    severity scale:
        "low"    — 1–1 failures
        "medium" — 2–4 failures
        "high"   — 5+ failures
    """

    cluster_id: str
    cluster_key: str
    lane_id: str
    failure_mode: str
    failure_count: int
    sample_packet_ids: list[str]
    collections_affected: list[str]
    avg_support_coverage: float
    avg_citation_completeness: float
    avg_exact_match_drift: float
    severity: str
    rca_summary: str
    first_seen_at: float
    last_seen_at: float


class RcaAggregator:
    """Aggregate ShadowEvalResults into RCA clusters.

    Clusters by (lane_id, lane_regression_tag).
    Thread-safe.  In-memory.  Future-run only.
    """

    _SEVERITY_HIGH_THRESHOLD = 5
    _SEVERITY_MEDIUM_THRESHOLD = 2

    def __init__(self) -> None:
        self._results: list["ShadowEvalResult"] = []
        self._lock = threading.Lock()

    def ingest(self, result: "ShadowEvalResult") -> None:
        """Add a graded result for aggregation."""
        with self._lock:
            self._results.append(result)

    def clusters(self) -> list[RcaCluster]:
        """Compute current RCA clusters from all ingested failing results.

        Only WARN and FAIL results are clustered.  PASS results are not included.

        Returns:
            List of RcaCluster objects sorted by failure_count descending.
        """
        with self._lock:
            failing = [r for r in self._results if r.overall_grade in ("WARN", "FAIL")]

        if not failing:
            return []

        groups: dict[str, list["ShadowEvalResult"]] = defaultdict(list)
        for r in failing:
            tag = r.lane_regression_tag or "UNKNOWN"
            key = f"{r.lane_id or 'unknown'}|{tag}"
            groups[key].append(r)

        clusters: list[RcaCluster] = []
        for key, members in groups.items():
            lane_id = members[0].lane_id or "unknown"
            tag = members[0].lane_regression_tag or "UNKNOWN"
            collections = sorted({m.collection for m in members if m.collection})
            n = len(members)
            avg_cov = round(sum(m.support_coverage for m in members) / n, 4)
            avg_cit = round(sum(m.citation_completeness for m in members) / n, 4)
            avg_drift = round(sum(m.exact_match_drift for m in members) / n, 4)

            if n >= self._SEVERITY_HIGH_THRESHOLD:
                severity = "high"
            elif n >= self._SEVERITY_MEDIUM_THRESHOLD:
                severity = "medium"
            else:
                severity = "low"

            clusters.append(
                RcaCluster(
                    cluster_id=f"rca-{hashlib.sha256(key.encode()).hexdigest()[:12]}",
                    cluster_key=key,
                    lane_id=lane_id,
                    failure_mode=tag,
                    failure_count=n,
                    sample_packet_ids=[m.packet_id for m in members[:10]],
                    collections_affected=collections,
                    avg_support_coverage=avg_cov,
                    avg_citation_completeness=avg_cit,
                    avg_exact_match_drift=avg_drift,
                    severity=severity,
                    rca_summary=_build_rca_summary(lane_id, tag, n, avg_cov, avg_cit, collections),
                    first_seen_at=min(m.graded_at for m in members),
                    last_seen_at=max(m.graded_at for m in members),
                )
            )

        return sorted(clusters, key=lambda c: c.failure_count, reverse=True)

    def result_count(self) -> int:
        with self._lock:
            return len(self._results)

    def clear(self) -> None:
        with self._lock:
            self._results.clear()


def _build_rca_summary(
    lane: str,
    tag: str,
    count: int,
    avg_cov: float,
    avg_cit: float,
    collections: list[str],
) -> str:
    col_str = ", ".join(collections) if collections else "unknown"
    likely_cause = {
        "ABSTAIN_MISSED": "evidence quality below governance threshold",
        "ESCALATION_MISSED": "contradiction detection or escalation logic drift",
        "WEAK_SUPPORT_WRONG": "threshold or classification constant changed",
        "GROUNDEDNESS_FAIL": "citation quality bar or grounded_replayable logic drift",
        "EXACT_MATCH_DRIFT": "retrieval surface change affecting exact-match leg",
    }.get(tag, "unknown root cause — manual review required")
    return (
        f"Lane '{lane}' produced {count} '{tag}' failure(s) "
        f"(avg_coverage={avg_cov:.3f}, avg_citation={avg_cit:.3f}, "
        f"collections=[{col_str}]). "
        f"Likely cause: {likely_cause}."
    )


__all__ = ["RcaCluster", "RcaAggregator"]
