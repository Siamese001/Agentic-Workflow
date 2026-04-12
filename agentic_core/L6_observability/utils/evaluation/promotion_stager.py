"""
agentic_core/L6_observability/utils/evaluation/promotion_stager.py

Promotion stager — stages future-run promotion candidates from RCA clusters.

STAGING ONLY.  No UWG commit.  No durable writes.  No L4 access.
Completed runs remain untouched.

PromotionCandidate.classification:
    HOLD    — cluster below threshold; parked for continued monitoring.
    PROPOSE — meets failure-count + severity threshold; ready for future-run rule
              change proposal.  NOT yet committed through UWG.
"""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING

from agentic_core.L2_execution.utils.providers import get_clock

if TYPE_CHECKING:
    from agentic_core.L6_observability.utils.evaluation.rca_aggregator import RcaCluster

_PROPOSE_MIN_FAILURES = 3
_PROPOSE_MIN_SEVERITY_ORDER = {"low": 0, "medium": 1, "high": 2}
_PROPOSE_MIN_SEVERITY_LEVEL = 1  # "medium"


@dataclass(frozen=True)
class PromotionCandidate:
    """Staged future-run promotion candidate.  Not yet committed through UWG.

    Fields
    ------
    classification:
        "HOLD"    — below threshold; continue monitoring.
        "PROPOSE" — meets threshold; ready to propose rule change in a future run.
    baseline_drift_findings:
        Human-readable list of observed deviations from governance baseline.
    suggested_changes:
        List of dicts: {parameter, current_value, proposed_value, rationale}.
    replay_references:
        Sample packet IDs for replay/investigation (first 5 from cluster).
    """

    candidate_id: str
    cluster_id: str
    cluster_key: str
    classification: str
    baseline_drift_findings: tuple[str, ...]
    suggested_changes: tuple[dict, ...]
    rationale: str
    replay_references: tuple[str, ...]
    staged_at: float


class PromotionStager:
    """Stage promotion candidates from RCA clusters.  No UWG writes."""

    def __init__(self) -> None:
        self._candidates: list[PromotionCandidate] = []
        self._lock = threading.Lock()

    def stage(self, cluster: "RcaCluster") -> PromotionCandidate:
        """Convert an RCA cluster into a staged promotion candidate.

        Args:
            cluster: RcaCluster from RcaAggregator.clusters().

        Returns:
            PromotionCandidate — staged but NOT committed through UWG.
        """
        classification = _classify(cluster)
        findings = _build_findings(cluster)
        suggestions = _build_suggestions(cluster)
        rationale = _build_rationale(cluster, classification)

        candidate = PromotionCandidate(
            candidate_id=f"pc-{uuid.uuid4().hex[:12]}",
            cluster_id=cluster.cluster_id,
            cluster_key=cluster.cluster_key,
            classification=classification,
            baseline_drift_findings=tuple(findings),
            suggested_changes=tuple(suggestions),
            rationale=rationale,
            replay_references=tuple(cluster.sample_packet_ids[:5]),
            staged_at=get_clock().now_epoch(),
        )
        with self._lock:
            self._candidates.append(candidate)
        return candidate

    def pending_candidates(self) -> list[PromotionCandidate]:
        with self._lock:
            return list(self._candidates)

    def clear(self) -> None:
        with self._lock:
            self._candidates.clear()


def _classify(cluster: "RcaCluster") -> str:
    severity_level = _PROPOSE_MIN_SEVERITY_ORDER.get(cluster.severity, 0)
    if cluster.failure_count >= _PROPOSE_MIN_FAILURES and severity_level >= _PROPOSE_MIN_SEVERITY_LEVEL:
        return "PROPOSE"
    return "HOLD"


def _build_findings(cluster: "RcaCluster") -> list[str]:
    findings = [
        f"Failure mode: {cluster.failure_mode} ({cluster.failure_count} occurrence(s), severity={cluster.severity})",
        f"Lane: {cluster.lane_id or 'unknown'}",
        f"Avg support_coverage: {cluster.avg_support_coverage:.3f} (thresholds: ABSTAIN=0.30, REFINE=0.60)",
        f"Avg citation_completeness: {cluster.avg_citation_completeness:.3f} (threshold: 0.50)",
        f"Avg exact_match_drift: {cluster.avg_exact_match_drift:+.3f}",
    ]
    if cluster.collections_affected:
        findings.append(f"Collections affected: {', '.join(cluster.collections_affected)}")
    return findings


def _build_suggestions(cluster: "RcaCluster") -> list[dict]:
    suggestions: list[dict] = []
    if cluster.failure_mode == "ABSTAIN_MISSED" and cluster.avg_support_coverage > 0.0:
        proposed = round(cluster.avg_support_coverage * 0.9, 2)
        suggestions.append(
            {
                "parameter": "abstain_coverage_threshold",
                "current_value": 0.30,
                "proposed_value": proposed,
                "rationale": (
                    f"Avg coverage {cluster.avg_support_coverage:.3f} consistently above "
                    f"current threshold — may indicate calibration drift"
                ),
            }
        )
    elif cluster.failure_mode == "GROUNDEDNESS_FAIL":
        proposed = round(cluster.avg_citation_completeness * 0.85, 2)
        suggestions.append(
            {
                "parameter": "grounded_citation_threshold",
                "current_value": 0.50,
                "proposed_value": proposed,
                "rationale": ("Repeated groundedness failures suggest citation quality bar drift"),
            }
        )
    elif cluster.failure_mode == "EXACT_MATCH_DRIFT":
        suggestions.append(
            {
                "parameter": "exact_match_baseline_ratio",
                "current_value": 0.0,
                "proposed_value": round(cluster.avg_support_coverage, 2),
                "rationale": "Persistent exact-match drift suggests baseline needs updating",
            }
        )
    if not suggestions:
        suggestions.append(
            {
                "parameter": "review_required",
                "current_value": None,
                "proposed_value": None,
                "rationale": f"Manual review needed for {cluster.failure_mode} failures",
            }
        )
    return suggestions


def _build_rationale(cluster: "RcaCluster", classification: str) -> str:
    if classification == "PROPOSE":
        return (
            f"Cluster '{cluster.cluster_key}' crossed the promotion threshold "
            f"({cluster.failure_count} failures, severity={cluster.severity}). "
            f"Proposed for future-run rule adjustment. NOT yet committed through UWG."
        )
    return (
        f"Cluster '{cluster.cluster_key}' below promotion threshold "
        f"({cluster.failure_count} failures, severity={cluster.severity}). "
        f"Staged as HOLD for continued monitoring."
    )


__all__ = ["PromotionCandidate", "PromotionStager"]
