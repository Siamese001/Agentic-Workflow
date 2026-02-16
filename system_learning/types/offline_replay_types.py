"""Offline Replay & Golden Trace Harness — Wave 7.0.13 (Schema Lock Only).

Deterministic, pure-function pipeline runner that composes existing L7 builders
into a full artifact chain: signals → aggregate → proposal → evaluation →
approval → decision → change_package → rollout_plan.

NO runtime behavior changes.  NO mutation logic.  NO automatic application.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any, Literal

from agentic_core.L0_routing.types.v15_p2_types import SemanticClockSnapshot
from system_learning.enforcement.determinism import deterministic_json
from system_learning.types.app_signal_types import (
    AppSignalAggregateArtifact,
    AppSignalEventArtifact,
    aggregate_app_signals,
)
from system_learning.types.meta_learning_types import (
    MetaLearningApprovalArtifact,
    MetaLearningChangePackageArtifact,
    MetaLearningDecisionArtifact,
    MetaLearningEvaluationArtifact,
    MetaLearningProposalArtifact,
    build_meta_learning_approval,
    build_meta_learning_change_package,
    build_meta_learning_decision,
    build_meta_learning_evaluation,
    build_meta_learning_proposal,
)
from system_learning.types.rollout_types import (
    MetaLearningRolloutPlanArtifact,
    build_meta_learning_rollout_plan,
)

# =============================================================================
# §Wave7.0.13 — Replay: Signals → Aggregate
# =============================================================================


def replay_app_signals_to_aggregate(
    *,
    events: Sequence[AppSignalEventArtifact],
    metric_name: str,
    app_id: str,
    window_id: str,
    baseline_selector: Callable[[AppSignalEventArtifact], bool],
    candidate_selector: Callable[[AppSignalEventArtifact], bool],
    evidence_hash: str,
    semantic_clock: SemanticClockSnapshot,
) -> AppSignalAggregateArtifact:
    """Replay raw signal events into an aggregate artifact.

    Pure delegate to aggregate_app_signals() with catalog enforcement.
    """
    return aggregate_app_signals(
        app_id=app_id,
        window_id=window_id,
        metric_name=metric_name,
        events=events,
        baseline_selector=baseline_selector,
        candidate_selector=candidate_selector,
        evidence_hash=evidence_hash,
        semantic_clock=semantic_clock,
    )


# =============================================================================
# §Wave7.0.13 — Replay: Aggregate → Rollout Plan (full pipeline)
# =============================================================================


@dataclass(frozen=True)
class OfflineReplayBundle:
    """Immutable container for all artifacts produced by an offline replay.

    When the pipeline is blocked (verdict != IMPROVE or approval == REJECT),
    decision.decision == "REJECT" and change_package / rollout_plan are None.
    """

    aggregate: AppSignalAggregateArtifact
    proposal: MetaLearningProposalArtifact
    evaluation: MetaLearningEvaluationArtifact
    approval: MetaLearningApprovalArtifact
    decision: MetaLearningDecisionArtifact
    change_package: MetaLearningChangePackageArtifact | None
    rollout_plan: MetaLearningRolloutPlanArtifact | None


def replay_aggregate_to_rollout(
    *,
    aggregate: AppSignalAggregateArtifact,
    proposer: str,
    target_component: str,
    before: dict[str, Any],
    after: dict[str, Any],
    evaluator: str,
    dataset_id: str,
    eval_evidence_hash: str,
    approver: str,
    approval_decision: Literal["APPROVE", "REJECT"],
    approval_rationale: str,
    rollout_strategy: str,
    rollout_invariants: list[str],
    rollout_max_duration_minutes: int,
    canary_percent: int | None = None,
    semantic_clock: SemanticClockSnapshot,
    policy_config_hash: str | None = None,
) -> OfflineReplayBundle:
    """Compose existing builders in strict order to produce a full artifact chain.

    Fail-closed: if evaluation verdict != IMPROVE or approval == REJECT,
    decision will be REJECT and change_package / rollout_plan will be None.

    Returns
    -------
    OfflineReplayBundle
        All artifacts produced by the replay.
    """
    proposal = build_meta_learning_proposal(
        semantic_clock=semantic_clock,
        proposer=proposer,
        target_component=target_component,
        before=before,
        after=after,
        metric_name=aggregate.metric_name,
        baseline=aggregate.baseline_value,
        candidate=aggregate.candidate_value,
        evidence_hash=aggregate.evidence_hash,
        policy_config_hash=policy_config_hash,
    )

    evaluation = build_meta_learning_evaluation(
        proposal=proposal,
        evaluator=evaluator,
        dataset_id=dataset_id,
        baseline=aggregate.baseline_value,
        candidate=aggregate.candidate_value,
        evidence_hash=eval_evidence_hash,
        policy_config_hash=policy_config_hash,
    )

    approval = build_meta_learning_approval(
        evaluation=evaluation,
        approver=approver,
        decision=approval_decision,
        rationale=approval_rationale,
        policy_config_hash=policy_config_hash,
    )

    decision = build_meta_learning_decision(
        proposal=proposal,
        evaluation=evaluation,
        approval=approval,
        semantic_clock=semantic_clock,
        policy_config_hash=policy_config_hash,
    )

    change_package: MetaLearningChangePackageArtifact | None = None
    rollout_plan: MetaLearningRolloutPlanArtifact | None = None

    if decision.decision == "ALLOW_TO_APPLY":
        change_package = build_meta_learning_change_package(
            proposal=proposal,
            evaluation=evaluation,
            approval=approval,
            decision=decision,
            target_component=target_component,
            change_spec=after,
            semantic_clock=semantic_clock,
            policy_config_hash=policy_config_hash,
        )
        rollout_plan = build_meta_learning_rollout_plan(
            change_package,
            strategy=rollout_strategy,
            canary_percent=canary_percent,
            invariants=rollout_invariants,
            max_duration_minutes=rollout_max_duration_minutes,
            semantic_clock=semantic_clock,
            policy_config_hash=policy_config_hash,
        )

    return OfflineReplayBundle(
        aggregate=aggregate,
        proposal=proposal,
        evaluation=evaluation,
        approval=approval,
        decision=decision,
        change_package=change_package,
        rollout_plan=rollout_plan,
    )


# =============================================================================
# §Wave7.0.13 — Render: canonical JSON bundle
# =============================================================================


def render_offline_replay_bundle(bundle: OfflineReplayBundle) -> str:
    """Render a canonical JSON string of all artifacts in the bundle.

    Returns
    -------
    str
        Deterministic JSON (sorted keys, compact separators).
    """
    d: dict[str, object] = {
        "aggregate": bundle.aggregate.to_dict(),
        "approval": bundle.approval.to_dict(),
        "change_package": bundle.change_package.to_dict() if bundle.change_package else None,
        "decision": bundle.decision.to_dict(),
        "evaluation": bundle.evaluation.to_dict(),
        "proposal": bundle.proposal.to_dict(),
        "rollout_plan": bundle.rollout_plan.to_dict() if bundle.rollout_plan else None,
    }
    return deterministic_json(d)
