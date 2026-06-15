"""Retrieval Drift — measures retrieval result stability across index rebuilds.

Implements the G8 eval axis: "retrieval drift post-reindex".  When the
underlying index is rebuilt (e.g. after re-chunking or embedding model swap),
the same queries should return substantially the same top-K results.
Significant drift indicates non-determinism or regression.

Design:
  - ``DriftResult`` captures per-query drift metrics.
  - ``RetrievalDriftAnalyzer`` compares two sets of benchmark results
    (baseline vs. post-reindex) and computes Jaccard similarity, rank
    correlation (Kendall τ), and position-shift statistics.
  - Intended for CI: fail if drift exceeds configurable threshold.
"""

from __future__ import annotations

import logging
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# DriftResult — per-query drift metrics
# ---------------------------------------------------------------------------


@dataclass
class DriftResult:
    """Drift metrics for a single query.

    Attributes
    ----------
    query : str
        The query string.
    baseline_ids : list[str]
        Chunk IDs from the baseline run (ordered by rank).
    post_ids : list[str]
        Chunk IDs from the post-reindex run (ordered by rank).
    jaccard_similarity : float
        |intersection| / |union| of the two ID sets (0–1).
    kendall_tau : float
        Rank correlation between the two orderings (-1 to 1).
        Computed only on the intersection of IDs.
    mean_position_shift : float
        Average absolute rank shift for IDs present in both sets.
    ids_lost : list[str]
        IDs in baseline but not in post-reindex.
    ids_gained : list[str]
        IDs in post-reindex but not in baseline.
    """

    query: str
    baseline_ids: list[str]
    post_ids: list[str]
    jaccard_similarity: float = 0.0
    kendall_tau: float = 0.0
    mean_position_shift: float = 0.0
    ids_lost: list[str] = field(default_factory=list)
    ids_gained: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# DriftReport — aggregate drift across all queries
# ---------------------------------------------------------------------------


@dataclass
class DriftReport:
    """Aggregate drift report across all queries.

    Attributes
    ----------
    total_queries : int
        Number of queries analyzed.
    avg_jaccard : float
        Average Jaccard similarity across queries.
    avg_tau : float
        Average Kendall τ across queries.
    avg_position_shift : float
        Average mean position shift across queries.
    max_position_shift : float
        Worst single-query mean position shift.
    queries_with_high_drift : list[str]
        Queries where Jaccard < threshold.
    """

    total_queries: int = 0
    avg_jaccard: float = 0.0
    avg_tau: float = 0.0
    avg_position_shift: float = 0.0
    max_position_shift: float = 0.0
    queries_with_high_drift: list[str] = field(default_factory=list)


@dataclass
class DriftAlert:
    """Operator-facing drift alert summary for JSON artifacts."""

    run_id: str
    generated_at: str
    status: str
    threshold: float
    avg_jaccard: float
    high_drift_queries: list[str] = field(default_factory=list)
    message: str = ""


# ---------------------------------------------------------------------------
# RetrievalDriftAnalyzer
# ---------------------------------------------------------------------------


class RetrievalDriftAnalyzer:
    """Analyzes retrieval drift between baseline and post-reindex results.

    Args:
        jaccard_threshold : float
            Below this Jaccard similarity, a query is flagged as high-drift.
    """

    def __init__(self, jaccard_threshold: float = 0.7) -> None:
        if not 0.0 <= jaccard_threshold <= 1.0:
            raise ValueError(f"jaccard_threshold must be in [0, 1], got {jaccard_threshold}")
        self._jaccard_threshold = jaccard_threshold

    def compute_drift(
        self,
        query: str,
        baseline_ids: list[str],
        post_ids: list[str],
    ) -> DriftResult:
        """Compute drift for a single query.

        Args:
            query: The query string.
            baseline_ids: Ordered chunk IDs from baseline run.
            post_ids: Ordered chunk IDs from post-reindex run.

        Returns:
            ``DriftResult`` with computed metrics.

        Raises:
            TypeError: If baseline_ids or post_ids are not lists.
        """
        if not isinstance(baseline_ids, list):
            raise TypeError(f"baseline_ids must be list, got {type(baseline_ids).__name__}")
        if not isinstance(post_ids, list):
            raise TypeError(f"post_ids must be list, got {type(post_ids).__name__}")
        baseline_set = set(baseline_ids)
        post_set = set(post_ids)
        intersection = baseline_set & post_set
        union = baseline_set | post_set

        # Jaccard similarity
        jaccard = len(intersection) / len(union) if union else 1.0

        # IDs lost / gained
        ids_lost = sorted(baseline_set - post_set)
        ids_gained = sorted(post_set - baseline_set)

        # Position shift (for IDs present in both)
        baseline_rank = {cid: idx for idx, cid in enumerate(baseline_ids)}
        post_rank = {cid: idx for idx, cid in enumerate(post_ids)}
        shifts: list[float] = []
        for cid in intersection:
            shift = abs(baseline_rank[cid] - post_rank[cid])
            shifts.append(float(shift))
        mean_shift = sum(shifts) / len(shifts) if shifts else 0.0

        # Kendall τ on intersection
        tau = self._kendall_tau(baseline_ids, post_ids, intersection)

        return DriftResult(
            query=query,
            baseline_ids=baseline_ids,
            post_ids=post_ids,
            jaccard_similarity=jaccard,
            kendall_tau=tau,
            mean_position_shift=mean_shift,
            ids_lost=ids_lost,
            ids_gained=ids_gained,
        )

    def compute_report(
        self,
        results: list[DriftResult],
    ) -> DriftReport:
        """Aggregate drift results into a report.

        Args:
            results: Per-query drift results.

        Returns:
            ``DriftReport`` with aggregate metrics.
        """
        if not results:
            return DriftReport()

        n = len(results)
        avg_jaccard = sum(r.jaccard_similarity for r in results) / n
        avg_tau = sum(r.kendall_tau for r in results) / n
        avg_shift = sum(r.mean_position_shift for r in results) / n
        max_shift = max(r.mean_position_shift for r in results)
        high_drift = [
            r.query
            for r in results
            if r.jaccard_similarity < self._jaccard_threshold
        ]

        return DriftReport(
            total_queries=n,
            avg_jaccard=avg_jaccard,
            avg_tau=avg_tau,
            avg_position_shift=avg_shift,
            max_position_shift=max_shift,
            queries_with_high_drift=high_drift,
        )

    @staticmethod
    def _kendall_tau(
        baseline: list[str],
        post: list[str],
        intersection: set[str],
    ) -> float:
        """Compute Kendall τ on the intersection of two ranked lists."""
        if len(intersection) < 2:
            return 1.0 if intersection else 0.0

        # Build rank maps for intersection items only
        base_rank = {cid: idx for idx, cid in enumerate(baseline) if cid in intersection}
        post_rank = {cid: idx for idx, cid in enumerate(post) if cid in intersection}

        # Normalize ranks to 0..n-1
        sorted_base = sorted(base_rank, key=lambda c: base_rank[c])
        sorted_post = sorted(post_rank, key=lambda c: post_rank[c])

        base_norm = {cid: i for i, cid in enumerate(sorted_base)}
        post_norm = {cid: i for i, cid in enumerate(sorted_post)}

        # Count concordant / discordant pairs
        items = list(intersection)
        concordant = 0
        discordant = 0
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                a, b = items[i], items[j]
                diff_base = base_norm[a] - base_norm[b]
                diff_post = post_norm[a] - post_norm[b]
                if diff_base * diff_post > 0:
                    concordant += 1
                elif diff_base * diff_post < 0:
                    discordant += 1

        total = concordant + discordant
        if total == 0:
            return 1.0
        return (concordant - discordant) / total


def build_drift_alert(
    report: DriftReport,
    *,
    threshold: float = 0.7,
    run_id: str = "manual",
) -> DriftAlert:
    """Build an advisory alert from an aggregate drift report.

    ``threshold`` is the minimum acceptable average Jaccard similarity. The
    per-query high-drift list still comes from ``RetrievalDriftAnalyzer`` so
    callers can tune query-level and aggregate thresholds separately.
    """

    if not 0.0 <= threshold <= 1.0:
        raise ValueError(f"threshold must be in [0, 1], got {threshold}")

    high_drift_queries = sorted(report.queries_with_high_drift)
    status = (
        "alert"
        if high_drift_queries or (report.total_queries > 0 and report.avg_jaccard < threshold)
        else "pass"
    )
    prefix = "[DRIFT-ALERT]" if status == "alert" else "[DRIFT-CLEAR]"
    message = (
        f"{prefix} {len(high_drift_queries)} high-drift queries; "
        f"avg_jaccard={report.avg_jaccard:.4f}; threshold={threshold:.4f}"
    )
    return DriftAlert(
        run_id=run_id,
        generated_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        status=status,
        threshold=threshold,
        avg_jaccard=report.avg_jaccard,
        high_drift_queries=high_drift_queries,
        message=message,
    )


def write_drift_report(
    report: DriftReport,
    path: Path,
    *,
    alert: DriftAlert | None = None,
) -> dict[str, Any]:
    """Write a drift report artifact and return the serialized payload."""

    alert = alert or build_drift_alert(report)
    payload = {
        "report": asdict(report),
        "alert": asdict(alert),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


__all__ = [
    "DriftAlert",
    "DriftReport",
    "DriftResult",
    "RetrievalDriftAnalyzer",
    "build_drift_alert",
    "write_drift_report",
]
