"""
agentic_core/L6_observability/utils/evaluation/shadow_eval_pipeline.py

L6 shadow evaluation pipeline coordinator.

Full cycle: AsyncEvalIngester.drain() → ShadowEvalGrader.grade() →
            RcaAggregator.ingest() → PromotionStager.stage()

Future-run only.  In-memory only.  No durable writes.  No L4 access.
No new packages.
"""

from __future__ import annotations

from typing import Any

from agentic_core.L6_observability.utils.evaluation.async_eval_packet import (
    AsyncEvalPacket,
    get_async_eval_ingester,
    reset_async_eval_ingester,
)
from agentic_core.L6_observability.utils.evaluation.promotion_stager import (
    PromotionCandidate,
    PromotionStager,
)
from agentic_core.L6_observability.utils.evaluation.rca_aggregator import (
    RcaAggregator,
    RcaCluster,
)
from agentic_core.L6_observability.utils.evaluation.shadow_eval_grader import (
    ShadowEvalGrader,
    ShadowEvalResult,
)


class L6ShadowEvalPipeline:
    """Full L6 shadow evaluation pipeline coordinator.

    Drains the AsyncEvalIngester → grades each packet → aggregates into
    RCA clusters → stages promotion candidates.

    No durable writes.  No live-run mutation.  No L4 access.

    Usage::

        pipeline = L6ShadowEvalPipeline()
        # ... evidence-governed lanes run and emit packets via ingest_eval_packet() ...
        summary = pipeline.run_cycle(baseline=loaded_baseline_dict)
        clusters = pipeline.clusters()
        candidates = pipeline.candidates()
    """

    def __init__(self) -> None:
        self._ingester = get_async_eval_ingester()
        self._grader = ShadowEvalGrader()
        self._aggregator = RcaAggregator()
        self._stager = PromotionStager()
        self._graded: list[ShadowEvalResult] = []

    def run_cycle(
        self,
        max_packets: int = 200,
        baseline: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Drain → grade → aggregate → stage one evaluation cycle.

        Idempotent for the same ingester contents: calling twice drains once,
        then returns empty on the second call.

        Args:
            max_packets: Max packets to drain from the ingester per cycle.
            baseline:    Loaded evidence_governance_baseline.json (optional).

        Returns:
            Cycle summary dict:
                packets_processed   — int
                results_graded      — int
                pass_count          — int
                warn_count          — int
                fail_count          — int
                clusters            — list[RcaCluster]
                candidates_staged   — int (total pending, all cycles)
                new_candidates      — list[PromotionCandidate] staged this cycle
        """
        packets = self._ingester.drain(max_packets=max_packets)
        if not packets:
            return {
                "packets_processed": 0,
                "results_graded": 0,
                "pass_count": 0,
                "warn_count": 0,
                "fail_count": 0,
                "clusters": [],
                "candidates_staged": len(self._stager.pending_candidates()),
                "new_candidates": [],
            }

        results: list[ShadowEvalResult] = []
        for pkt in packets:
            result = self._grader.grade(pkt, baseline=baseline)
            self._aggregator.ingest(result)
            self._graded.append(result)
            results.append(result)

        clusters = self._aggregator.clusters()

        existing_cluster_ids = {c.cluster_id for c in self._stager.pending_candidates()}
        new_candidates: list[PromotionCandidate] = []
        for cluster in clusters:
            if cluster.cluster_id not in existing_cluster_ids:
                candidate = self._stager.stage(cluster)
                new_candidates.append(candidate)

        return {
            "packets_processed": len(packets),
            "results_graded": len(results),
            "pass_count": sum(1 for r in results if r.overall_grade == "PASS"),
            "warn_count": sum(1 for r in results if r.overall_grade == "WARN"),
            "fail_count": sum(1 for r in results if r.overall_grade == "FAIL"),
            "clusters": clusters,
            "candidates_staged": len(self._stager.pending_candidates()),
            "new_candidates": new_candidates,
        }

    def summary(self) -> dict[str, Any]:
        """Full pipeline summary across all cycles."""
        clusters = self._aggregator.clusters()
        candidates = self._stager.pending_candidates()
        return {
            "total_graded": len(self._graded),
            "pass": sum(1 for r in self._graded if r.overall_grade == "PASS"),
            "warn": sum(1 for r in self._graded if r.overall_grade == "WARN"),
            "fail": sum(1 for r in self._graded if r.overall_grade == "FAIL"),
            "cluster_count": len(clusters),
            "pending_candidates": len(candidates),
            "propose_count": sum(1 for c in candidates if c.classification == "PROPOSE"),
            "hold_count": sum(1 for c in candidates if c.classification == "HOLD"),
        }

    def all_graded(self) -> list[ShadowEvalResult]:
        return list(self._graded)

    def clusters(self) -> list[RcaCluster]:
        return self._aggregator.clusters()

    def candidates(self) -> list[PromotionCandidate]:
        return self._stager.pending_candidates()

    def reset(self) -> None:
        """Reset all state (for testing)."""
        self._aggregator.clear()
        self._stager.clear()
        self._graded.clear()
        reset_async_eval_ingester()
        self._ingester = get_async_eval_ingester()


__all__ = ["L6ShadowEvalPipeline"]
