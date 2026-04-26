"""03.8 L3 Governance — concurrency, quality-loop, fallback, completion, sealing.

Pure functions per 03.8 §PHASE 2-5:

- ``govern_concurrency(ledger, blueprint) -> ConcurrencyPlan``
- ``govern_quality_loop(ledger, plan, current_score, current_iteration) -> StopLoopReceipt``
- ``apply_fallback_control(state, fallback_chain, reason) -> FallbackCascadeState``
- ``run_completion_test(ledger, blueprint, context_bus) -> WorkflowCompletionTest``
- ``seal_workflow_package(...) -> SealedWorkflowPackage``
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from . import L3DoctrineContractError
from .contracts_l3_6 import ManagedWorkflowBlueprint
from .contracts_l3_7 import L3ContextBus, L3StateLedger, NodeState
from .contracts_l3_8 import (
    CompletionStatus,
    ConcurrencyPlan,
    CostLatencyTokenSummary,
    FallbackCascadeState,
    QualityLoopPlan,
    SealedWorkflowPackage,
    WorkflowCompletionTest,
    WorkflowOutcomeClass,
)


def _digest(payload: object, prefix: str) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"{prefix}:{hashlib.sha256(encoded).hexdigest()}"


# ---------------------------------------------------------------------------
# Concurrency
# ---------------------------------------------------------------------------


def govern_concurrency(
    ledger: L3StateLedger,
    blueprint: ManagedWorkflowBlueprint,
    *,
    max_parallelism: int = 4,
    resource_ceiling: int = 16,
) -> ConcurrencyPlan:
    """03.8 PHASE 2 govern_concurrency.

    Builds a deterministic concurrency plan: by default everything is serial
    (single parallel group of one) since blueprint nodes are sequenced. A
    stronger heuristic could group nodes that share no edge dependency; that
    is intentionally out of scope for the doctrine module — callers may
    extend with their own policy and still satisfy ``ConcurrencyPlan``'s shape.
    """
    if not isinstance(ledger, L3StateLedger):
        raise L3DoctrineContractError("govern_concurrency ledger must be L3StateLedger")
    if not isinstance(blueprint, ManagedWorkflowBlueprint):
        raise L3DoctrineContractError(
            "govern_concurrency blueprint must be ManagedWorkflowBlueprint",
        )
    if max_parallelism < 1:
        raise L3DoctrineContractError("max_parallelism must be >= 1")
    if resource_ceiling < 1:
        raise L3DoctrineContractError("resource_ceiling must be >= 1")

    # Deterministic ordering by declared node order
    node_order = [n.node_id for n in blueprint.nodes]
    parallel_groups = tuple((nid,) for nid in node_order)
    payload = {
        "workflow_id": ledger.workflow_id,
        "node_order": node_order,
        "max_parallelism": max_parallelism,
    }
    plan_hash = _digest(payload, "conc")
    return ConcurrencyPlan(
        workflow_id=ledger.workflow_id,
        parallel_groups=parallel_groups,
        serial_only_nodes=tuple(node_order),
        max_parallelism=max_parallelism,
        branch_policy="serial_unless_parallel_safe",
        join_policy="deterministic_order",
        race_prevention_policy="advisory_lock_per_node",
        shard_failure_policy="emit_safe_partial",
        deterministic_join_order=tuple(node_order),
        resource_ceiling=resource_ceiling,
        concurrency_plan_hash=plan_hash,
    )


# ---------------------------------------------------------------------------
# Quality loop
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class StopLoopReceipt:
    """Receipt explaining why a quality loop should stop."""

    loop_id: str
    stop: bool
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.loop_id, str) or not self.loop_id:
            raise L3DoctrineContractError("StopLoopReceipt.loop_id must be non-empty str")
        if not isinstance(self.stop, bool):
            raise L3DoctrineContractError("StopLoopReceipt.stop must be bool")
        if not isinstance(self.reason, str) or not self.reason:
            raise L3DoctrineContractError("StopLoopReceipt.reason must be non-empty str")


def govern_quality_loop(
    plan: QualityLoopPlan,
    *,
    current_score: float,
    current_iteration: int,
    last_score: float | None = None,
    remaining_budget: float = 1.0,
) -> StopLoopReceipt:
    """03.8 PHASE 3 govern_quality_loop -> StopLoopReceipt.

    Stops when:
    - current_score >= quality_threshold
    - current_iteration >= max_iterations
    - remaining_budget <= 0.0
    - oscillation detected (last_score within 1% of current_score across two iters)
    """
    if not isinstance(plan, QualityLoopPlan):
        raise L3DoctrineContractError("govern_quality_loop plan must be QualityLoopPlan")
    if isinstance(current_score, bool) or not isinstance(current_score, (int, float)):
        raise L3DoctrineContractError("current_score must be float")
    if current_score != current_score or current_score < 0.0 or current_score > 1.0:
        raise L3DoctrineContractError("current_score must be in [0,1]")
    if isinstance(current_iteration, bool) or not isinstance(current_iteration, int):
        raise L3DoctrineContractError("current_iteration must be int")
    if current_iteration < 0:
        raise L3DoctrineContractError("current_iteration must be >= 0")

    if current_score >= plan.quality_threshold:
        return StopLoopReceipt(
            loop_id=plan.loop_id,
            stop=True,
            reason=f"threshold_reached:{current_score}>={plan.quality_threshold}",
        )
    if current_iteration >= plan.max_iterations:
        return StopLoopReceipt(
            loop_id=plan.loop_id,
            stop=True,
            reason=f"max_iterations_reached:{current_iteration}>={plan.max_iterations}",
        )
    if remaining_budget <= 0.0:
        return StopLoopReceipt(
            loop_id=plan.loop_id,
            stop=True,
            reason="budget_exhausted",
        )
    if last_score is not None and abs(current_score - last_score) < 0.01:
        return StopLoopReceipt(
            loop_id=plan.loop_id,
            stop=True,
            reason="oscillation_or_no_material_improvement",
        )
    return StopLoopReceipt(
        loop_id=plan.loop_id,
        stop=False,
        reason="continue",
    )


# ---------------------------------------------------------------------------
# Fallback cascade
# ---------------------------------------------------------------------------


def apply_fallback_control(
    state: FallbackCascadeState,
    *,
    next_candidate: str,
    reason_code: str,
    provider_alternative: str = "",
) -> FallbackCascadeState:
    """03.8 PHASE 4 apply_fallback_control.

    Returns a new ``FallbackCascadeState`` advanced by one fallback step.
    Rejects calls that would attempt a candidate not in ``fallback_chain``.
    """
    if not isinstance(state, FallbackCascadeState):
        raise L3DoctrineContractError(
            "apply_fallback_control state must be FallbackCascadeState",
        )
    if not isinstance(next_candidate, str) or not next_candidate:
        raise L3DoctrineContractError("next_candidate must be non-empty str")
    if not isinstance(reason_code, str) or not reason_code:
        raise L3DoctrineContractError("reason_code must be non-empty str (no silent fallback)")
    if next_candidate not in state.fallback_chain:
        raise L3DoctrineContractError(
            f"next_candidate {next_candidate!r} not in fallback_chain {state.fallback_chain!r}",
        )

    new_attempts = state.attempted_fallbacks + (next_candidate,)
    new_reasons = state.fallback_reason_codes + (reason_code,)
    new_alternatives = (
        state.provider_tool_alternatives + (provider_alternative,)
        if provider_alternative
        else state.provider_tool_alternatives
    )
    payload = {
        "workflow_id": state.workflow_id,
        "attempts": list(new_attempts),
        "depth": state.fallback_depth + 1,
    }
    new_hash = _digest(payload, "fb")
    return FallbackCascadeState(
        workflow_id=state.workflow_id,
        fallback_chain=state.fallback_chain,
        fallback_depth=state.fallback_depth + 1,
        attempted_fallbacks=new_attempts,
        current_fallback_candidate=next_candidate,
        fallback_reason_codes=new_reasons,
        provider_tool_alternatives=new_alternatives,
        tier_cascade_state=state.tier_cascade_state,
        circuit_breaker_status=state.circuit_breaker_status,
        fallback_hash=new_hash,
        no_silent_fallback_assertion=True,
    )


# ---------------------------------------------------------------------------
# Completion test
# ---------------------------------------------------------------------------


def run_completion_test(
    ledger: L3StateLedger,
    blueprint: ManagedWorkflowBlueprint,
    context_bus: L3ContextBus,
) -> WorkflowCompletionTest:
    """03.8 PHASE 5 run_completion_test.

    Pure function from current ledger + blueprint + context_bus to a
    ``WorkflowCompletionTest``.
    """
    if not isinstance(ledger, L3StateLedger):
        raise L3DoctrineContractError("run_completion_test ledger must be L3StateLedger")
    if not isinstance(blueprint, ManagedWorkflowBlueprint):
        raise L3DoctrineContractError(
            "run_completion_test blueprint must be ManagedWorkflowBlueprint",
        )
    if not isinstance(context_bus, L3ContextBus):
        raise L3DoctrineContractError(
            "run_completion_test context_bus must be L3ContextBus",
        )

    state_map = {nid: state for nid, state in ledger.node_states}
    sealed_states = {NodeState.SUCCEEDED, NodeState.SEALED}
    failed_states = {NodeState.FAILED_TERMINAL, NodeState.REJECTED}
    paused_states = {NodeState.PAUSED_HITL}
    needs_help_states = {NodeState.NEEDS_HELP}

    all_sealed = all(state_map.get(n.node_id, NodeState.NOT_READY) in sealed_states for n in blueprint.nodes)
    any_failed = any(state_map.get(n.node_id, NodeState.NOT_READY) in failed_states for n in blueprint.nodes)
    any_paused = any(state_map.get(n.node_id, NodeState.NOT_READY) in paused_states for n in blueprint.nodes)
    any_needs_help = any(
        state_map.get(n.node_id, NodeState.NOT_READY) in needs_help_states for n in blueprint.nodes
    )
    has_contradictions = bool(context_bus.contradiction_flags)
    has_gaps = bool(context_bus.unresolved_gaps)
    has_partial = bool(context_bus.carried_l2_artifact_refs)

    if any_paused:
        completion_status = CompletionStatus.NEEDS_HITL_PAUSE
    elif any_failed and not has_partial:
        completion_status = CompletionStatus.FAILED_TERMINAL
    elif any_failed and has_partial:
        completion_status = CompletionStatus.SAFE_PARTIAL_READY
    elif any_needs_help:
        completion_status = CompletionStatus.NEEDS_NEXT_NODE
    elif all_sealed and not has_gaps:
        completion_status = CompletionStatus.COMPLETE
    elif all_sealed and has_gaps:
        completion_status = CompletionStatus.COMPLETE_DEGRADED
    elif not all_sealed:
        completion_status = CompletionStatus.NEEDS_NEXT_NODE
    else:
        completion_status = CompletionStatus.ABSTAIN_RECOMMENDED

    payload = {
        "workflow_id": ledger.workflow_id,
        "ledger_hash": ledger.ledger_hash,
        "completion_status": completion_status.value,
    }
    completion_hash = _digest(payload, "comp")

    return WorkflowCompletionTest(
        workflow_id=ledger.workflow_id,
        all_required_nodes_sealed=all_sealed,
        mandatory_branches_resolved=all_sealed,
        joins_complete=all_sealed,
        required_support_satisfied=not has_gaps,
        contradictions_labeled=has_contradictions,
        unresolved_gaps_carried_forward=has_gaps,
        route_success_conditions_satisfied=all_sealed and not has_gaps,
        mutation_proposal_only=True,
        hitl_pause_resolved_or_carried=not any_paused,
        budget_status="ok" if ledger.remaining_budget > 0 else "exhausted",
        best_partial_available=has_partial,
        completion_status=completion_status,
        completion_hash=completion_hash,
    )


# ---------------------------------------------------------------------------
# Seal workflow package
# ---------------------------------------------------------------------------


def seal_workflow_package(
    *,
    ledger: L3StateLedger,
    blueprint: ManagedWorkflowBlueprint,
    context_bus: L3ContextBus,
    completion: WorkflowCompletionTest,
    request_id: str,
    run_id: str,
    trace_root: str,
    cost_summary: CostLatencyTokenSummary,
    branch_join_manifest: str = "default",
    fallback_manifest: str = "default",
    quality_loop_manifest: str = "default",
) -> SealedWorkflowPackage:
    """03.8 PHASE 5 seal_workflow_package.

    Composes a SealedWorkflowPackage from current state. Caller MUST verify
    ``completion.completion_status`` is one of COMPLETE / COMPLETE_DEGRADED /
    SAFE_PARTIAL_READY / FAILED_TERMINAL / ABSTAIN_RECOMMENDED before invoking.
    """
    sealable = {
        CompletionStatus.COMPLETE,
        CompletionStatus.COMPLETE_DEGRADED,
        CompletionStatus.SAFE_PARTIAL_READY,
        CompletionStatus.FAILED_TERMINAL,
        CompletionStatus.ABSTAIN_RECOMMENDED,
    }
    if completion.completion_status not in sealable:
        raise L3DoctrineContractError(
            f"seal_workflow_package refused: completion_status={completion.completion_status.value}"
            " is not sealable",
        )

    outcome_class = {
        CompletionStatus.COMPLETE: WorkflowOutcomeClass.CLEAN,
        CompletionStatus.COMPLETE_DEGRADED: WorkflowOutcomeClass.DEGRADED,
        CompletionStatus.SAFE_PARTIAL_READY: WorkflowOutcomeClass.PARTIAL,
        CompletionStatus.FAILED_TERMINAL: WorkflowOutcomeClass.FAILED,
        CompletionStatus.ABSTAIN_RECOMMENDED: WorkflowOutcomeClass.ABSTAIN,
    }[completion.completion_status]

    completed_node_refs = tuple(
        n.node_id
        for n in blueprint.nodes
        if {nid: state for nid, state in ledger.node_states}.get(n.node_id, NodeState.NOT_READY)
        in {NodeState.SUCCEEDED, NodeState.SEALED}
    )

    payload = {
        "workflow_id": ledger.workflow_id,
        "graph_hash": blueprint.graph_hash,
        "ledger_hash": ledger.ledger_hash,
        "completion_hash": completion.completion_hash,
        "outcome": outcome_class.value,
    }
    package_hash = _digest(payload, "pkg")
    package_id = _digest({"hash": package_hash}, "pkgid")

    return SealedWorkflowPackage(
        sealed_workflow_package_id=package_id,
        workflow_id=ledger.workflow_id,
        route_contract_id=ledger.route_contract_id,
        request_id=request_id,
        run_id=run_id,
        trace_root=trace_root,
        policy_hash=ledger.policy_hash,
        blueprint_hash=ledger.blueprint_hash,
        replay_key=ledger.replay_key,
        graph_hash=blueprint.graph_hash,
        ledger_hash=ledger.ledger_hash,
        completed_node_refs=completed_node_refs,
        sealed_l2_artifact_refs=context_bus.carried_l2_artifact_refs,
        prompt_artifact_refs=context_bus.carried_prompt_artifact_refs,
        evidence_contract_refs=context_bus.carried_evidence_refs,
        branch_join_manifest=branch_join_manifest,
        fallback_manifest=fallback_manifest,
        quality_loop_manifest=quality_loop_manifest,
        contradiction_flags=context_bus.contradiction_flags,
        unresolved_gaps=context_bus.unresolved_gaps,
        best_partial_artifact_refs=context_bus.carried_l2_artifact_refs,
        proposed_state_diff_refs=tuple(),
        hitl_packet_refs=context_bus.carried_human_review_refs,
        cost_latency_token_summary=cost_summary,
        workflow_outcome_class=outcome_class,
        route_success_condition_status=(
            "satisfied" if completion.route_success_conditions_satisfied else "unsatisfied"
        ),
        package_hash=package_hash,
        hmac_sig="",
        mutation_proposal_only_assertion=True,
        exit_review_required=True,
        no_durable_commit_assertion=True,
    )


__all__ = [
    "StopLoopReceipt",
    "apply_fallback_control",
    "govern_concurrency",
    "govern_quality_loop",
    "run_completion_test",
    "seal_workflow_package",
]
