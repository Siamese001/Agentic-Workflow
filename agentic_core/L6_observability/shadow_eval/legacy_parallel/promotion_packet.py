"""Seal staged promotion candidates into future-run promotion packets."""

from __future__ import annotations

import dataclasses
import hashlib
import json
import time
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, ClassVar

get_clock: Any = None

try:
    from agentic_core.L2_execution.utils.providers import (
        get_clock,
    )  # guardian: allow-layer-violation -- L6 observability module uses L2 execution type; intentional cross-layer instrumentation dependency
except ImportError:
    get_clock = None

if TYPE_CHECKING:
    from agentic_core.L6_observability.shadow_eval.legacy_parallel.promotion_gauntlet import GauntletResult
    from agentic_core.L6_observability.shadow_eval.legacy_parallel.promotion_stager import PromotionCandidate
    from agentic_core.L6_observability.shadow_eval.legacy_parallel.rca_aggregator import RcaCluster


class ApprovalState(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    COMMITTED = "COMMITTED"


_DEST_CLASS_MAP: dict[str, str] = {
    "ABSTAIN_MISSED": "evidence_threshold.abstain_coverage",
    "GROUNDEDNESS_FAIL": "evidence_threshold.citation_quality",
    "EXACT_MATCH_DRIFT": "evidence_threshold.baseline_ratio",
    "WEAK_SUPPORT_WRONG": "evidence_threshold.disposition",
    "ESCALATION_MISSED": "safety_policy.escalation_gate",
    "UNKNOWN": "evidence_threshold.generic",
}


def _now_epoch() -> float:
    if get_clock is not None:
        try:
            return float(get_clock().now_epoch())
        except (
            AttributeError,
            RuntimeError,
            TypeError,
            ValueError,
        ):  # guardian: allow-silent-swallow -- clock epoch fallback: non-fatal, time.time() used as fallback
            pass
    return time.time()


def _stable_id(prefix: str, payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return f"{prefix}-{hashlib.sha256(encoded).hexdigest()[:16]}"


@dataclass(frozen=True)
class PromotionPacket:
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
    def packetize(
        self,
        candidate: "PromotionCandidate",
        cluster: "RcaCluster",
        gauntlet_result: "GauntletResult",
    ) -> PromotionPacket:
        from agentic_core.L6_observability.shadow_eval.legacy_parallel.promotion_gauntlet import VERDICT_APPROVE

        if gauntlet_result.verdict != VERDICT_APPROVE:
            raise ValueError(
                f"Cannot packetize: gauntlet verdict is {gauntlet_result.verdict!r}, expected {VERDICT_APPROVE!r}"
            )
        return self._build_packet(candidate, cluster, approval_state=ApprovalState.PENDING, pending=False)

    def packetize_pending(self, candidate: "PromotionCandidate", cluster: "RcaCluster") -> PromotionPacket:
        return self._build_packet(candidate, cluster, approval_state=ApprovalState.PENDING, pending=True)

    def _build_packet(
        self,
        candidate: "PromotionCandidate",
        cluster: "RcaCluster",
        *,
        approval_state: ApprovalState,
        pending: bool,
    ) -> PromotionPacket:
        dest_class = _DEST_CLASS_MAP.get(
            getattr(cluster, "failure_mode", "UNKNOWN"), "evidence_threshold.generic"
        )
        rollout_meta = _build_rollout_metadata(candidate, cluster)
        rollback_meta = _build_rollback_metadata(rollout_meta)
        replay_refs = tuple(candidate.replay_references)
        replay_digest = (
            hashlib.sha256("|".join(sorted(replay_refs)).encode("utf-8")).hexdigest()[:16]
            if replay_refs
            else "0" * 16
        )
        baseline_refs = (
            f"cluster_key={cluster.cluster_key}",
            f"failure_mode={cluster.failure_mode}",
            f"severity={cluster.severity}",
        )
        digest_short = replay_digest[:8]
        version_tag = f"{candidate.candidate_id[:8]}-{digest_short}"
        edition = f"future-run/{'pending' if pending else 'v1'}/{version_tag}"
        packet_payload = {
            "candidate_id": candidate.candidate_id,
            "cluster_key": candidate.cluster_key,
            "version_tag": version_tag,
            "target_destination_class": dest_class,
            "replay_digest": replay_digest,
            "pending": pending,
        }
        return PromotionPacket(
            packet_id=_stable_id("pp", packet_payload),
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
            sealed_at=_now_epoch(),
            approval_state=approval_state,
        )


def _build_rollout_metadata(candidate: "PromotionCandidate", cluster: "RcaCluster") -> dict:
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
    return {
        "parameter": rollout_meta["parameter"],
        "revert_to_value": rollout_meta["current_value"],
        "from_proposed_value": rollout_meta["proposed_value"],
        "rollback_trigger": "manual_approval_required",
        "cluster_id": rollout_meta.get("cluster_id", "unknown"),
    }


_VALID_TRANSITIONS: frozenset[tuple[ApprovalState, ApprovalState]] = frozenset(
    {
        (ApprovalState.PENDING, ApprovalState.APPROVED),
        (ApprovalState.PENDING, ApprovalState.REJECTED),
        (ApprovalState.APPROVED, ApprovalState.COMMITTED),
        (ApprovalState.APPROVED, ApprovalState.REJECTED),
    }
)


def transition_approval_state(packet: PromotionPacket, new_state: ApprovalState) -> PromotionPacket:
    current = packet.approval_state
    if (current, new_state) not in _VALID_TRANSITIONS:
        valid_targets = [target.value for source, target in _VALID_TRANSITIONS if source == current]
        raise ValueError(
            f"Invalid approval state transition: {current.value!r} → {new_state.value!r}. Valid targets from {current.value!r}: {valid_targets}"
        )
    return dataclasses.replace(packet, approval_state=new_state)


__all__ = [
    "ApprovalState",
    "PromotionPacket",
    "PromotionPacketizer",
    "transition_approval_state",
]
