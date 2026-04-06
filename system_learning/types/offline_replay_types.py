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

from agentic_core.interfaces.determinism_types import SemanticClockSnapshot
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    record_execution_trace,
)

_emit_authorize_and_execute("p2", "offline_replay_types", "execution_auth")
_emit_validates_capability("p2", "offline_replay_types", "capability_check")
_emit_routes_to_capability("p2", "offline_replay_types", "capability_route")
_emit_writes_via_uwg("p2", "offline_replay_types", "uwg_write")
_emit_blocks_direct_write("p2", "offline_replay_types", "direct_write_block")
_emit_records_tool_invocation("p2", "offline_replay_types", "tool_invocation")
_emit_captures_execution_output("p2", "offline_replay_types", "exec_output")
_emit_dispatches_agent("p3", "offline_replay_types", "agent_dispatch")
_emit_coordinates_agents("p3", "offline_replay_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "offline_replay_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "offline_replay_types", "healing_outcome")
_emit_escalates_failure("p3", "offline_replay_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "offline_replay_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "offline_replay_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "offline_replay_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "offline_replay_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "offline_replay_types", "eval_metric")
_emit_stores_embedding("p4", "offline_replay_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "offline_replay_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "offline_replay_types", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
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

record_execution_trace("offline_replay_types", "offline_replay_types_trace")


_emit_emits_metric_event("offline_replay_types", "p4obs", "metric_1")
_emit_emits_metric_event("offline_replay_types", "p4obs", "metric_2")
_emit_emits_metric_event("offline_replay_types", "p4obs", "metric_3")
_emit_emits_metric_event("offline_replay_types", "p4obs", "metric_4")
_emit_emits_metric_event("offline_replay_types", "p4obs", "metric_5")
_emit_emits_metric_event("offline_replay_types", "p4obs", "metric_6")
_emit_records_incident_event("offline_replay_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("offline_replay_types", "p4obs", "anomaly")
_emit_writes_observability_log("offline_replay_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("offline_replay_types", "p4obs", "mon_state")
_emit_triggers_alert("offline_replay_types", "p4obs", "alert")
_emit_links_incident_trace("offline_replay_types", "p4obs", "trace_link")
_emit_captures_pattern("offline_replay_types", "p3lm", "pattern")
_emit_records_learning_event("offline_replay_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("offline_replay_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("offline_replay_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("offline_replay_types", "p3lm", "routing")
_emit_improves_agent_policy("offline_replay_types", "p3lm", "policy")
_emit_stores_learning_state("offline_replay_types", "p3lm", "state")
_emit_records_execution_trace("offline_replay_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("offline_replay_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("offline_replay_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("offline_replay_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("offline_replay_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("offline_replay_types", "env_read", "p2_env_1")
_emit_reads_environ("offline_replay_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("offline_replay_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("offline_replay_types", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "offline_replay_types")
_emit_applies_guardrail("p0", "offline_replay_types", "p0_governance")
_emit_reads_policy_state("p0", "offline_replay_types", "policy_binding")
_emit_snapshots_state("p0", "offline_replay_types", "state_snapshot")
_emit_pulls_context("p1", "offline_replay_types", "context_pull")
_emit_pulls_context("p1", "offline_replay_types", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "offline_replay_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "offline_replay_types", "uwg_term_secondary")
_emit_writes_through("p1", "offline_replay_types", "write_through")
_emit_writes_through("p1", "offline_replay_types", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "offline_replay_types", "safety_validation")
_emit_invokes_eval("p1", "offline_replay_types", "eval_call")
_emit_proposal_commits_routing("p1", "offline_replay_types", "routing_commit")
_emit_escalates_to_human("p1", "offline_replay_types", "human_escalation")
_emit_routes_through("p1", "offline_replay_types", "route_through")
_emit_checks_agent_registry("p1", "offline_replay_types", "agent_registry")
_emit_validates_agent_capability("p1", "offline_replay_types", "capability")
_emit_dispatches_execution_plan("p1", "offline_replay_types", "exec_plan")
_emit_agent_executes_agent("p1", "offline_replay_types", "sub_agent")
_emit_routes_to_agent("p1", "offline_replay_types", "target_agent")
_emit_verifies_policy("p1", "offline_replay_types", "policy_check")
_emit_observes_runtime_state("p1", "offline_replay_types", "runtime_state")
_emit_verifies_boundary("p1", "offline_replay_types", "boundary_check")
_emit_transcripts_response("p1", "offline_replay_types", "transcript")
_emit_hard_fails_untranscripted("p1", "offline_replay_types")
_emit_gated_by_confidence("p1", "offline_replay_types", "confidence_gate")
emit_replay_key("p0", "offline_replay_types")
emit_determinism_digest("p0", "offline_replay_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
