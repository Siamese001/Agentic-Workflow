"""
agentic_core/L6_observability/utils/evaluation/promotion_packet.py

Promotion packetizer — converts APPROVE_FOR_PACKETIZATION gauntlet results into
sealed promotion packets ready for future-run governed handoff.

Packet fields:
  - packet_id / edition / version_tag
  - candidate_id / cluster_key
  - target_destination_class   — parameter category derived from cluster failure_mode
  - rationale                  — from PromotionCandidate
  - evidence_replay_references — packet IDs for shadow replay / investigation
  - baseline_regression_refs   — cluster_key + failure_mode for baseline comparison
  - rollout_metadata           — suggested parameter change (target + proposed value)
  - rollback_metadata          — reverse of the proposed change (safe revert spec)
  - replay_digest              — SHA-256 of evidence_replay_references (token binding)
  - sealed_at                  — monotonic epoch tick

Future-run only.  No durable writes.  No L4 access.  No UWG bypass.
Non-mutating until handed to the governed seam via GovernedHandoffAgent.
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, ClassVar

from agentic_core.L2_execution.utils.providers import get_clock

if TYPE_CHECKING:
    from agentic_core.L6_observability.utils.evaluation.promotion_gauntlet import GauntletResult
    from agentic_core.L6_observability.utils.evaluation.promotion_stager import PromotionCandidate
    from agentic_core.L6_observability.utils.evaluation.rca_aggregator import RcaCluster


class ApprovalState(str, Enum):
    """Approval lifecycle state of a PromotionPacket.

    PENDING   — Staged; awaiting commandant gauntlet review.
    APPROVED  — Gauntlet approved; ready for GovernedHandoffAgent / UWG commit.
    REJECTED  — Commandant rejected; no future-run change will be applied.
    COMMITTED — UWG commit completed; future-run parameter updated.

    State transitions (enforced by callers, not by this type):
        PENDING → APPROVED | REJECTED
        APPROVED → COMMITTED | REJECTED
    """

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    COMMITTED = "COMMITTED"


# Destination class map: failure_mode → parameter category
_DEST_CLASS_MAP: dict[str, str] = {
    "ABSTAIN_MISSED": "evidence_threshold.abstain_coverage",
    "GROUNDEDNESS_FAIL": "evidence_threshold.citation_quality",
    "EXACT_MATCH_DRIFT": "evidence_threshold.baseline_ratio",
    "WEAK_SUPPORT_WRONG": "evidence_threshold.disposition",
    "ESCALATION_MISSED": "safety_policy.escalation_gate",
    "UNKNOWN": "evidence_threshold.generic",
}


@dataclass(frozen=True)
class PromotionPacket:
    """Sealed future-run promotion packet.

    Non-mutating until handed to the governed UWG seam via GovernedHandoffAgent.

    Fields
    ------
    packet_id:
        Unique identifier for this packet.
    edition:
        Human-readable version tag (e.g. "future-run/v1/<digest[:8]>").
    version_tag:
        Short version string derived from candidate_id and replay_digest.
    candidate_id:
        Source PromotionCandidate.candidate_id.
    cluster_key:
        Source RcaCluster.cluster_key (lane|failure_mode).
    target_destination_class:
        Parameter category to apply the proposed change to.
    rationale:
        Human-readable justification for this promotion.
    evidence_replay_references:
        Packet IDs for shadow replay / investigation.
    baseline_regression_refs:
        Baseline references for regression comparison.
    rollout_metadata:
        {parameter, current_value, proposed_value, rationale, cluster_id,
         failure_count, severity} — the proposed future-run change.
    rollback_metadata:
        {parameter, revert_to_value, from_proposed_value, rollback_trigger,
         cluster_id} — safe reversal spec.
    replay_digest:
        SHA-256[:16] of sorted evidence_replay_references (for PromotionToken binding).
    sealed_at:
        Monotonic epoch tick at packetization time.
    """

    run_scope: ClassVar[str] = "FUTURE_RUN"

    packet_id: str
    edition: str
    version_tag: str
    candidate_id: str
    cluster_key: str
    target_destination_class: str
    rationale: str
    evidence_replay_references: tuple[str, ...]
    baseline_regression_refs: tuple[str, ...]
    rollout_metadata: dict
    rollback_metadata: dict
    replay_digest: str
    sealed_at: float
    approval_state: ApprovalState = ApprovalState.PENDING
    target_surface: str = ""


class PromotionPacketizer:
    """Converts approved gauntlet results into sealed PromotionPackets.

    No side effects.  No durable writes.  Future-run only.
    """

    def packetize(
        self,
        candidate: "PromotionCandidate",
        cluster: "RcaCluster",
        gauntlet_result: "GauntletResult",
    ) -> PromotionPacket:
        """Seal an approved candidate into a PromotionPacket.

        Args:
            candidate:       Approved PromotionCandidate from PromotionStager.
            cluster:         Source RcaCluster from RcaAggregator.
            gauntlet_result: GauntletResult with APPROVE_FOR_PACKETIZATION verdict.

        Returns:
            PromotionPacket — sealed.  Not yet handed to UWG.

        Raises:
            ValueError: If gauntlet_result.verdict != APPROVE_FOR_PACKETIZATION.
        """
        from agentic_core.L6_observability.utils.evaluation.promotion_gauntlet import (  # noqa: PLC0415
            VERDICT_APPROVE,
        )

        if gauntlet_result.verdict != VERDICT_APPROVE:
            raise ValueError(
                f"Cannot packetize: gauntlet verdict is {gauntlet_result.verdict!r}, "
                f"expected {VERDICT_APPROVE!r}"
            )

        dest_class = _DEST_CLASS_MAP.get(cluster.failure_mode, "evidence_threshold.generic")
        rollout_meta = _build_rollout_metadata(candidate, cluster)
        rollback_meta = _build_rollback_metadata(rollout_meta)
        replay_refs = candidate.replay_references
        replay_digest = hashlib.sha256("|".join(sorted(replay_refs)).encode("utf-8")).hexdigest()[:16]
        baseline_refs = (
            f"cluster_key={cluster.cluster_key}",
            f"failure_mode={cluster.failure_mode}",
            f"severity={cluster.severity}",
        )
        digest_short = replay_digest[:8]
        version_tag = f"{candidate.candidate_id[:8]}-{digest_short}"
        edition = f"future-run/v1/{version_tag}"

        return PromotionPacket(
            packet_id=f"pp-{uuid.uuid4().hex[:12]}",
            edition=edition,
            version_tag=version_tag,
            candidate_id=candidate.candidate_id,
            cluster_key=candidate.cluster_key,
            target_destination_class=dest_class,
            rationale=candidate.rationale,
            evidence_replay_references=replay_refs,
            baseline_regression_refs=tuple(baseline_refs),
            rollout_metadata=rollout_meta,
            rollback_metadata=rollback_meta,
            replay_digest=replay_digest,
            sealed_at=get_clock().now_epoch(),
        )


def _build_rollout_metadata(
    candidate: "PromotionCandidate",
    cluster: "RcaCluster",
) -> dict:
    """Extract the primary rollout change from suggested_changes."""
    if candidate.suggested_changes:
        primary = candidate.suggested_changes[0]
        return {
            "parameter": primary.get("parameter", "unknown"),
            "current_value": primary.get("current_value"),
            "proposed_value": primary.get("proposed_value"),
            "rationale": primary.get("rationale", ""),
            "cluster_id": cluster.cluster_id,
            "failure_count": cluster.failure_count,
            "severity": cluster.severity,
        }
    return {
        "parameter": "unknown",
        "current_value": None,
        "proposed_value": None,
        "rationale": "No suggested changes available",
        "cluster_id": cluster.cluster_id,
        "failure_count": cluster.failure_count,
        "severity": cluster.severity,
    }


def _build_rollback_metadata(rollout_meta: dict) -> dict:
    """Build a reverse rollback spec from the rollout metadata."""
    return {
        "parameter": rollout_meta["parameter"],
        "revert_to_value": rollout_meta["current_value"],
        "from_proposed_value": rollout_meta["proposed_value"],
        "rollback_trigger": "manual_approval_required",
        "cluster_id": rollout_meta.get("cluster_id", "unknown"),
    }


__all__ = ["ApprovalState", "PromotionPacket", "PromotionPacketizer"]
