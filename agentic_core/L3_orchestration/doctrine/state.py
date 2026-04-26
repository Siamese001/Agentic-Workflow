"""03.7 L3 State management — pure functions for ready-node selection,
step contract emission, and step result ingest.

Implements 03.7 §PHASE 2-4:

- ``select_next_ready_node(ledger, blueprint, context_bus) -> NodeReadinessDecision``
- ``emit_step_contract(decision, ledger, context_bus) -> L3StepContract``
- ``ingest_step_result(step_result, ledger) -> HandoffMergeReceipt``

All functions are pure; they return new objects but never mutate inputs.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict

from . import L3DoctrineContractError
from .contracts_l3_6 import (
    ManagedWorkflowBlueprint,
    WorkflowEdge,
    WorkflowNode,
    WorkflowNodeType,
)
from .contracts_l3_7 import (
    HandoffMergeReceipt,
    L3ContextBus,
    L3StateLedger,
    L3StepContract,
    NodeReadinessDecision,
    NodeState,
    StepInputs,
    StepResultIngest,
    StepResultStatus,
)


def _digest(payload: object, prefix: str) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"{prefix}:{hashlib.sha256(encoded).hexdigest()}"


def _node_state_map(ledger: L3StateLedger) -> dict[str, NodeState]:
    return {node_id: state for node_id, state in ledger.node_states}


def _attempt_count_map(ledger: L3StateLedger) -> dict[str, int]:
    return {node_id: count for node_id, count in ledger.attempt_counts}


def _incoming_edges(blueprint: ManagedWorkflowBlueprint, node_id: str) -> list[WorkflowEdge]:
    return [e for e in blueprint.edges if e.to_node == node_id]


def _is_dependency_satisfied(
    edge: WorkflowEdge,
    state_map: dict[str, NodeState],
) -> bool:
    upstream_state = state_map.get(edge.from_node, NodeState.NOT_READY)
    return upstream_state in {
        NodeState.SUCCEEDED,
        NodeState.SEALED,
        NodeState.DEGRADED,
        NodeState.SKIPPED,
    }


def select_next_ready_node(
    ledger: L3StateLedger,
    blueprint: ManagedWorkflowBlueprint,
    context_bus: L3ContextBus,
) -> NodeReadinessDecision:
    """03.7 §PHASE 2 select_next_ready_node.

    Returns a decision for the FIRST node in declared order whose dependencies
    are satisfied AND whose state is NOT_READY. If no node qualifies, returns
    a decision for the first not-yet-sealed node with ``ready=False`` and
    populated ``blocked_reasons``.
    """
    if not isinstance(ledger, L3StateLedger):
        raise L3DoctrineContractError(
            f"select_next_ready_node ledger must be L3StateLedger, got {type(ledger).__name__}",
        )
    if not isinstance(blueprint, ManagedWorkflowBlueprint):
        raise L3DoctrineContractError(
            f"select_next_ready_node blueprint must be ManagedWorkflowBlueprint, got {type(blueprint).__name__}",
        )
    if not isinstance(context_bus, L3ContextBus):
        raise L3DoctrineContractError(
            f"select_next_ready_node context_bus must be L3ContextBus, got {type(context_bus).__name__}",
        )

    state_map = _node_state_map(ledger)
    attempt_map = _attempt_count_map(ledger)

    # Look for the first NOT_READY/READY node whose dependencies are satisfied.
    for node in blueprint.nodes:
        cur_state = state_map.get(node.node_id, NodeState.NOT_READY)
        if cur_state in {NodeState.SUCCEEDED, NodeState.SEALED, NodeState.SKIPPED, NodeState.REJECTED}:
            continue
        if cur_state == NodeState.PAUSED_HITL:
            continue  # paused — wait for re-clearance externally
        incoming = _incoming_edges(blueprint, node.node_id)
        unsatisfied: list[str] = []
        satisfied: list[str] = []
        for edge in incoming:
            if _is_dependency_satisfied(edge, state_map):
                satisfied.append(edge.edge_id)
            else:
                unsatisfied.append(edge.edge_id)
        budget_ok = ledger.remaining_budget > 0.0 and ledger.remaining_slo > 0
        retry_ok = attempt_map.get(node.node_id, 0) < node.max_attempts
        ready = not unsatisfied and budget_ok and retry_ok

        blocked: list[str] = []
        if unsatisfied:
            blocked.append(f"unsatisfied_deps:{len(unsatisfied)}")
        if not budget_ok:
            blocked.append("budget_or_slo_exhausted")
        if not retry_ok:
            blocked.append("retry_limit_reached")

        payload = {
            "workflow_id": ledger.workflow_id,
            "node_id": node.node_id,
            "ready": ready,
            "satisfied": satisfied,
            "unsatisfied": unsatisfied,
            "ledger_hash": ledger.ledger_hash,
        }
        readiness_hash = _digest(payload, "rdy")
        return NodeReadinessDecision(
            decision_id=_digest({"id": readiness_hash}, "rdid"),
            workflow_id=ledger.workflow_id,
            node_id=node.node_id,
            ready=ready,
            blocked_reasons=tuple(blocked),
            satisfied_dependencies=tuple(satisfied),
            unsatisfied_dependencies=tuple(unsatisfied),
            required_evidence_refs=context_bus.carried_evidence_refs,
            required_policy_refs=tuple(),
            required_capability_refs=(node.capability_requirement,),
            budget_status="ok" if budget_ok else "exhausted",
            retry_status="ok" if retry_ok else "limit",
            fallback_status=f"depth={ledger.fallback_depth}",
            hitl_status="paused" if cur_state == NodeState.PAUSED_HITL else "none",
            readiness_hash=readiness_hash,
        )

    # No ready node and no further work — synthesize a "no work" decision.
    payload = {
        "workflow_id": ledger.workflow_id,
        "node_id": "<no_more_work>",
        "ready": False,
        "ledger_hash": ledger.ledger_hash,
    }
    readiness_hash = _digest(payload, "rdy")
    return NodeReadinessDecision(
        decision_id=_digest({"id": readiness_hash}, "rdid"),
        workflow_id=ledger.workflow_id,
        node_id="<no_more_work>",
        ready=False,
        blocked_reasons=("no_more_work",),
        satisfied_dependencies=tuple(),
        unsatisfied_dependencies=tuple(),
        required_evidence_refs=tuple(),
        required_policy_refs=tuple(),
        required_capability_refs=tuple(),
        budget_status="ok" if ledger.remaining_budget > 0 else "exhausted",
        retry_status="ok",
        fallback_status=f"depth={ledger.fallback_depth}",
        hitl_status="none",
        readiness_hash=readiness_hash,
    )


def _node_by_id(blueprint: ManagedWorkflowBlueprint, node_id: str) -> WorkflowNode:
    for n in blueprint.nodes:
        if n.node_id == node_id:
            return n
    raise L3DoctrineContractError(
        f"emit_step_contract: node_id={node_id!r} not found in blueprint",
    )


def emit_step_contract(
    decision: NodeReadinessDecision,
    ledger: L3StateLedger,
    blueprint: ManagedWorkflowBlueprint,
    context_bus: L3ContextBus,
    *,
    parent_route_id: str,
    route_digest: str,
    snapshot_id: str,
) -> L3StepContract:
    """03.7 §PHASE 3 emit_step_contract.

    Emits exactly one bounded step contract for the ``decision.node_id``.
    Caller MUST verify ``decision.ready`` is True.
    """
    if not isinstance(decision, NodeReadinessDecision):
        raise L3DoctrineContractError(
            "emit_step_contract requires NodeReadinessDecision",
        )
    if not decision.ready:
        raise L3DoctrineContractError(
            f"emit_step_contract refused: decision.ready=False, blocked_reasons={decision.blocked_reasons}",
        )

    node = _node_by_id(blueprint, decision.node_id)
    attempt_map = _attempt_count_map(ledger)
    attempt_id = f"a{attempt_map.get(node.node_id, 0) + 1:03d}"

    inputs = StepInputs(
        query_refs=context_bus.carried_query_refs,
        evidence_refs=context_bus.carried_evidence_refs,
        graph_refs=context_bus.carried_graph_refs,
        prompt_artifact_refs=context_bus.carried_prompt_artifact_refs,
        prior_artifact_refs=context_bus.carried_l2_artifact_refs,
    )

    expected_output = (
        "FinalEvidenceContract"
        if node.node_type == WorkflowNodeType.C0_GROUNDING_STEP
        else "CompiledPromptArtifact"
        if node.node_type == WorkflowNodeType.PROMPT_ASSEMBLY_STEP
        else "SealedL2Artifact"
    )
    payload = {
        "workflow_id": ledger.workflow_id,
        "node_id": decision.node_id,
        "attempt_id": attempt_id,
        "graph_hash": blueprint.graph_hash,
        "ledger_hash": ledger.ledger_hash,
        "decision_id": decision.decision_id,
    }
    contract_hash = _digest(payload, "step")
    contract_id = _digest({"hash": contract_hash}, "stepid")
    idempotency_key = _digest(
        {"node_id": decision.node_id, "attempt_id": attempt_id, "graph_hash": blueprint.graph_hash},
        "idem",
    )

    return L3StepContract(
        step_contract_id=contract_id,
        workflow_id=ledger.workflow_id,
        node_id=decision.node_id,
        attempt_id=attempt_id,
        parent_route_id=parent_route_id,
        route_digest=route_digest,
        policy_hash=ledger.policy_hash,
        blueprint_hash=ledger.blueprint_hash,
        snapshot_id=snapshot_id,
        replay_key=ledger.replay_key,
        idempotency_key=idempotency_key,
        node_type=node.node_type,
        current_work_order=node.current_ask,
        inputs=inputs,
        expected_output_contract=expected_output,
        capability_token_requirement=node.capability_requirement,
        sandbox_envelope_requirement=node.sandbox_requirement,
        timeout_ms=node.timeout_ms,
        retry_policy=node.retry_policy,
        fallback_permission=node.fallback_policy,
        telemetry_keys=(
            f"workflow_id={ledger.workflow_id}",
            f"node_id={decision.node_id}",
            f"attempt_id={attempt_id}",
        ),
        expected_receipts=(
            "step_invocation_receipt",
            "policy_compliance_receipt",
        ),
        step_contract_hash=contract_hash,
        no_durable_commit_authority=True,
    )


def ingest_step_result(
    step_result: StepResultIngest,
    *,
    workflow_id: str,
    node_id: str,
) -> HandoffMergeReceipt:
    """03.7 §PHASE 4 ingest_step_result -> HandoffMergeReceipt.

    Determines the new node state from the step status. Does NOT mutate the
    ledger directly; the caller composes a new ``L3StateLedger`` using this
    receipt. The ``node_id`` is required because ``StepResultIngest`` only
    carries the contract id; the caller knows the binding.
    """
    if not isinstance(step_result, StepResultIngest):
        raise L3DoctrineContractError(
            "ingest_step_result requires StepResultIngest",
        )
    if not isinstance(node_id, str) or not node_id:
        raise L3DoctrineContractError("ingest_step_result requires non-empty node_id")

    new_state = {
        StepResultStatus.SUCCESS: NodeState.SUCCEEDED,
        StepResultStatus.DEGRADED: NodeState.DEGRADED,
        StepResultStatus.FAILED: NodeState.FAILED_TERMINAL,
        StepResultStatus.NEEDS_HELP: NodeState.NEEDS_HELP,
        StepResultStatus.PAUSED_HITL: NodeState.PAUSED_HITL,
    }[step_result.status]

    node_id_hint = node_id
    payload = {
        "workflow_id": workflow_id,
        "step_contract_id": step_result.step_contract_id,
        "ingest_hash": step_result.ingest_hash,
        "new_state": new_state.value,
    }
    receipt_id = _digest(payload, "merge")

    contradictions: tuple[str, ...] = tuple()
    if (
        step_result.status in {StepResultStatus.FAILED, StepResultStatus.DEGRADED}
        and step_result.proposed_state_diff_refs
    ):
        contradictions = ("proposed_state_diff_present_with_failure",)

    return HandoffMergeReceipt(
        receipt_id=receipt_id,
        workflow_id=workflow_id,
        node_id=node_id_hint,
        new_state=new_state,
        reason_codes=(f"status:{step_result.status.value}",),
        preserved_lineage_refs=step_result.replay_receipt_refs,
        contradiction_flags=contradictions,
        durable_write_attempted=False,
    )


def initial_ledger(
    blueprint: ManagedWorkflowBlueprint,
    *,
    policy_hash: str,
    blueprint_hash: str,
    replay_key: str,
    route_contract_id: str,
    initial_budget: float,
    initial_slo_ms: int,
) -> L3StateLedger:
    """Helper to build a fresh L3StateLedger with all nodes NOT_READY.

    Useful for tests and for orchestrator init paths.
    """
    if not isinstance(blueprint, ManagedWorkflowBlueprint):
        raise L3DoctrineContractError(
            f"initial_ledger blueprint must be ManagedWorkflowBlueprint, got {type(blueprint).__name__}",
        )
    if isinstance(initial_budget, bool) or not isinstance(initial_budget, (int, float)):
        raise L3DoctrineContractError("initial_budget must be float")
    if initial_budget != initial_budget or initial_budget < 0.0:
        raise L3DoctrineContractError("initial_budget must be >= 0 and finite")
    if isinstance(initial_slo_ms, bool) or not isinstance(initial_slo_ms, int) or initial_slo_ms < 0:
        raise L3DoctrineContractError("initial_slo_ms must be int >= 0")

    node_states = tuple(
        sorted(((n.node_id, NodeState.NOT_READY) for n in blueprint.nodes), key=lambda p: p[0])
    )
    attempt_counts = tuple(sorted(((n.node_id, 0) for n in blueprint.nodes), key=lambda p: p[0]))
    payload = {
        "workflow_id": blueprint.workflow_id,
        "graph_hash": blueprint.graph_hash,
        "policy_hash": policy_hash,
        "blueprint_hash": blueprint_hash,
        "replay_key": replay_key,
        "node_states": [(nid, st.value) for nid, st in node_states],
    }
    ledger_hash = _digest(payload, "ledger")
    return L3StateLedger(
        workflow_id=blueprint.workflow_id,
        route_contract_id=route_contract_id,
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
        replay_key=replay_key,
        graph_hash=blueprint.graph_hash,
        node_states=node_states,
        edge_states=tuple(),
        branch_states=tuple(),
        join_states=tuple(),
        attempt_counts=attempt_counts,
        retry_counts=tuple(sorted(((n.node_id, 0) for n in blueprint.nodes), key=lambda p: p[0])),
        fallback_depth=0,
        remaining_budget=float(initial_budget),
        remaining_slo=initial_slo_ms,
        checkpoints=tuple(),
        paused_packets=tuple(),
        reason_codes=tuple(),
        ledger_hash=ledger_hash,
    )


__all__ = [
    "emit_step_contract",
    "ingest_step_result",
    "initial_ledger",
    "select_next_ready_node",
]
