"""
agentic_core/L6_observability/utils/evaluation/shadow_eval_pipeline.py

L6 shadow evaluation pipeline coordinator.

Full cycle: AsyncEvalIngester.drain() → ShadowEvalGrader.grade() →
            RcaAggregator.ingest() → PromotionStager.stage()

Future-run only.  In-memory only.  No durable writes.  No L4 access.
No new packages.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agentic_core.L6_observability.utils.evaluation.governed_handoff import HandoffRecord
    from agentic_core.L6_observability.utils.evaluation.promotion_packet import PromotionPacket

from agentic_core.L6_observability.utils.evaluation.async_eval_packet import (
    AsyncEvalPacket,
    ShadowEvalPacket,
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
    ShadowGradeBundle,
    ShadowPacketGrader,
    bridge_to_shadow_eval_result,
)

logger = logging.getLogger(__name__)


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

    def run_shadow_packet_cycle(
        self,
        packets: list[ShadowEvalPacket],
        baseline: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Grade ShadowEvalPackets through outcome/trajectory/governance dimensions.

        Separate from run_cycle() which processes narrow AsyncEvalPackets from the
        BUS-T ingester.  This path handles the broader ShadowEvalPacket input built
        by build_shadow_eval_packet() after a current-run closure.

        Future-run only.  No live mutation.  No UWG call.

        Args:
            packets:  ShadowEvalPackets from build_shadow_eval_packet().
            baseline: Optional baseline dict for regression comparison.

        Returns:
            Cycle summary dict with same keys as run_cycle(), plus:
                shadow_grade_bundles — list[ShadowGradeBundle] (one per packet)
        """
        # Scope guard: all input packets must be future-run scoped.
        bad = [p for p in packets if getattr(p, "run_scope", None) != "FUTURE_RUN"]
        if bad:
            raise ValueError(
                f"run_shadow_packet_cycle: {len(bad)} packet(s) with run_scope != 'FUTURE_RUN'. "
                "Shadow evaluation is future-run only — never pass current-run artifacts."
            )

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
                "shadow_grade_bundles": [],
            }

        grader = ShadowPacketGrader()
        bundles: list[ShadowGradeBundle] = []
        results: list[ShadowEvalResult] = []

        for pkt in packets:
            bundle = grader.grade(pkt, baseline=baseline)
            result = bridge_to_shadow_eval_result(bundle)
            self._aggregator.ingest(result)
            self._graded.append(result)
            bundles.append(bundle)
            results.append(result)

        clusters = self._aggregator.clusters()

        existing_cluster_keys = {c.cluster_key for c in self._stager.pending_candidates()}
        new_candidates: list[PromotionCandidate] = []
        for cluster in clusters:
            if cluster.cluster_key not in existing_cluster_keys:
                candidate = self._stager.stage(cluster)
                new_candidates.append(candidate)

        cycle_summary = {
            "packets_processed": len(packets),
            "results_graded": len(results),
            "pass_count": sum(1 for r in results if r.overall_grade == "PASS"),
            "warn_count": sum(1 for r in results if r.overall_grade == "WARN"),
            "fail_count": sum(1 for r in results if r.overall_grade == "FAIL"),
            "clusters": clusters,
            "candidates_staged": len(self._stager.pending_candidates()),
            "new_candidates": new_candidates,
            "shadow_grade_bundles": bundles,
        }
        logger.info(
            "[L6ShadowEvalPipeline.run_shadow_packet_cycle] processed=%d pass=%d warn=%d fail=%d new_candidates=%d",
            cycle_summary["packets_processed"],
            cycle_summary["pass_count"],
            cycle_summary["warn_count"],
            cycle_summary["fail_count"],
            len(new_candidates),
        )
        return cycle_summary

    def approve_and_handoff(
        self,
        packet: "PromotionPacket",
        *,
        dry_run: bool = True,
    ) -> "tuple[PromotionPacket, HandoffRecord]":
        """Route an APPROVED PromotionPacket through the governed UWG handoff.

        Validates that the packet is in APPROVED state, calls
        GovernedHandoffAgent.handoff(), and advances to COMMITTED if the commit
        succeeds.  Remains APPROVED (with error recorded) if handoff fails.

        Commit reachability invariant
        -----------------------------
        COMMITTED state is only set when HandoffRecord.committed is True, which
        requires dry_run=False AND GovernedHandoffAgent receiving a successful
        PromotionAuthority.update_pointer_via_gateway() call.  There is no other
        code path that sets COMMITTED.

        Args:
            packet:   PromotionPacket with approval_state=APPROVED.
            dry_run:  If True (default), issue token and publish BUS T but skip
                      the real UWG commit (HandoffRecord.committed stays False).

        Returns:
            (final_packet, record):
              - final_packet is COMMITTED when record.committed is True.
              - final_packet stays APPROVED otherwise (inspect record.error).

        Raises:
            ValueError: If packet.approval_state != APPROVED.
        """
        from agentic_core.L6_observability.utils.evaluation.governed_handoff import (  # noqa: PLC0415
            GovernedHandoffAgent,
            HandoffRecord,
        )
        from agentic_core.L6_observability.utils.evaluation.promotion_packet import (  # noqa: PLC0415
            ApprovalState,
            transition_approval_state,
        )

        if packet.approval_state != ApprovalState.APPROVED:
            raise ValueError(
                f"approve_and_handoff requires approval_state=APPROVED; got {packet.approval_state!r}"
            )

        record: HandoffRecord = GovernedHandoffAgent().handoff(
            packet,
            dry_run=dry_run,
            approved=True,
        )

        if record.committed:
            final_packet = transition_approval_state(packet, ApprovalState.COMMITTED)
        else:
            final_packet = packet

        logger.info(
            "[L6ShadowEvalPipeline.approve_and_handoff] packet_id=%s approval_state=%s committed=%s error=%r",
            final_packet.packet_id,
            final_packet.approval_state.value,
            record.committed,
            record.error or "",
        )
        return final_packet, record

    def reset(self) -> None:
        """Reset all state (for testing)."""
        self._aggregator.clear()
        self._stager.clear()
        self._graded.clear()
        reset_async_eval_ingester()
        self._ingester = get_async_eval_ingester()


__all__ = ["L6ShadowEvalPipeline"]
