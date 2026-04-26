"""03.6 L3 ``build_l3_workflow()`` — workflow blueprint builder.

Pure function. No I/O. Deterministic given inputs.

Steps (03.6 §PHASE 2 DAG BUILDER):

1. validate_route_contract_is_managed
2. classify_execution_shape
3. extract_work_units_from_task_spec (heuristic, deterministic)
4. build_nodes
5. build_edges
6. mark serial/parallel eligibility (recorded in branch_policy/parallelism_policy)
7. assign C0/PA/L2/HITL step ownership
8. bind capability/sandbox requirements
9. bind retry/fallback/quality policies
10. emit WorkflowGraphManifest (graph_hash)
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict

from . import L3DoctrineContractError
from .contracts_l3_6 import (
    EdgeDependencyType,
    ExecutionShape,
    ExecutionShapeClassification,
    L3WorkflowInput,
    ManagedWorkflowBlueprint,
    WorkflowEdge,
    WorkflowNode,
    WorkflowNodeType,
)


def _digest(payload: object, prefix: str) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"{prefix}:{hashlib.sha256(encoded).hexdigest()}"


def _validate_route_contract_is_managed(workflow_input: L3WorkflowInput) -> None:
    """Step 1 — entry law (03.6 §ENTRY LAW)."""
    if workflow_input.selected_route_id != "R3R4_MANAGED_WORKFLOW":
        raise L3DoctrineContractError(
            f"L3 only operates on R3R4_MANAGED_WORKFLOW; got {workflow_input.selected_route_id}",
        )
    if not workflow_input.policy_hash or not workflow_input.blueprint_hash:
        raise L3DoctrineContractError(
            "L3WorkflowInput requires policy_hash and blueprint_hash",
        )


def _classify_execution_shape(
    workflow_input: L3WorkflowInput,
) -> ExecutionShapeClassification:
    """Step 2 — classify execution shape (heuristic, deterministic)."""
    blob = f"{workflow_input.task_spec_ref} {workflow_input.query_spec_ref}".lower()
    dep = " then " in blob or "depends on" in blob or "after" in blob
    branch = " or " in blob or "either" in blob
    join = "merge" in blob or "join" in blob or "consolidate" in blob
    staged = "stage" in blob or "phase" in blob or "step" in blob
    parallel = "parallel" in blob or "fan out" in blob or "all of" in blob
    hitl = bool(workflow_input.hitl_pause_points)
    checkpoint = "resume" in blob or "checkpoint" in blob
    eval_loop = "iterate" in blob or "refine" in blob or "evaluate" in blob
    ptc = "tool batch" in blob or "script" in blob

    structural = dep or branch or join or staged or parallel or hitl or checkpoint or eval_loop
    classification = ExecutionShape.MULTI_STEP_WORKFLOW if structural else ExecutionShape.DIRECT_STEP_PACKAGE

    payload = {
        "blob": blob,
        "structural": structural,
        "classification": classification.value,
    }
    classification_hash = _digest(payload, "shape")

    return ExecutionShapeClassification(
        classification_id=_digest({"id": classification_hash}, "cid"),
        classification=classification,
        why_not_single_step=(("dependency_chain",) if dep else ())
        + (("branching",) if branch else ())
        + (("join_required",) if join else ())
        + (("staged_evidence",) if staged else ()),
        why_not_workflow=(("no_structural_signals",) if not structural else ()),
        changing_step_contracts=(("step_evolves",) if dep or eval_loop else ()),
        dependency_chain_detected=dep,
        branching_detected=branch,
        join_detected=join,
        staged_evidence_required=staged,
        parallel_shards_detected=parallel,
        hitl_pause_resume_required=hitl,
        checkpoint_resume_required=checkpoint,
        evaluator_optimizer_loop_required=eval_loop,
        ptc_step_candidate_detected=ptc,
        classification_hash=classification_hash,
    )


def _build_nodes(
    workflow_input: L3WorkflowInput,
    classification: ExecutionShapeClassification,
) -> tuple[WorkflowNode, ...]:
    """Steps 3+4+7+8 — extract work units, build nodes, assign ownership."""
    nodes: list[WorkflowNode] = []

    # Standard pattern for a managed read+action workflow:
    # C0 -> PA -> L2_model_or_tool -> (optional EVAL_LOOP) -> (optional HITL) -> MERGE -> (optional L2_action)
    # Always at least: C0 grounding + PA + one L2 model step + MERGE.
    base_nodes = [
        ("n_c0_ground", WorkflowNodeType.C0_GROUNDING_STEP, "Ground evidence for current sub-ask"),
        ("n_pa_assemble", WorkflowNodeType.PROMPT_ASSEMBLY_STEP, "Assemble bounded prompt"),
        ("n_l2_model", WorkflowNodeType.L2_MODEL_STEP, "Bounded model synthesis"),
    ]
    for node_id, node_type, ask in base_nodes:
        nodes.append(
            WorkflowNode(
                node_id=node_id,
                node_type=node_type,
                current_ask=ask,
                required_inputs=("query_refs",)
                if node_type != WorkflowNodeType.PROMPT_ASSEMBLY_STEP
                else ("evidence_refs",),
                expected_outputs=("evidence_refs",)
                if node_type == WorkflowNodeType.C0_GROUNDING_STEP
                else ("prompt_artifact_refs",)
                if node_type == WorkflowNodeType.PROMPT_ASSEMBLY_STEP
                else ("l2_artifact_refs",),
                support_target=workflow_input.support_expectation or "SOURCE_BACKED_SUMMARY",
                capability_requirement=workflow_input.capability_class,
                sandbox_requirement=workflow_input.sandbox_class,
                max_attempts=2,
                timeout_ms=min(workflow_input.route_slo.max_latency_ms, 30_000),
                cost_budget=max(0.001, min(workflow_input.route_slo.max_cost / 4.0, 1.0)),
                retry_policy="exponential_backoff",
                fallback_policy="cascade_on_failure",
                ptc_allowed_if_l2_step=False,
            ),
        )

    if classification.evaluator_optimizer_loop_required:
        nodes.append(
            WorkflowNode(
                node_id="n_eval_loop",
                node_type=WorkflowNodeType.EVAL_LOOP_STEP,
                current_ask="Evaluate quality and decide whether to refine",
                required_inputs=("l2_artifact_refs",),
                expected_outputs=("quality_score",),
                support_target="NONE",
                capability_requirement=workflow_input.capability_class,
                sandbox_requirement=workflow_input.sandbox_class,
                max_attempts=workflow_input.max_iterations,
                timeout_ms=min(workflow_input.route_slo.max_latency_ms, 60_000),
                cost_budget=max(0.001, min(workflow_input.route_slo.max_cost / 4.0, 1.0)),
                retry_policy="bounded_loop",
                fallback_policy="stop_on_threshold",
            ),
        )

    if classification.hitl_pause_resume_required:
        nodes.append(
            WorkflowNode(
                node_id="n_hitl_pause",
                node_type=WorkflowNodeType.HITL_PAUSE_STEP,
                current_ask="Bounded human review of proposed action/evidence",
                required_inputs=("l2_artifact_refs",),
                expected_outputs=("human_review_refs",),
                support_target="NONE",
                capability_requirement="REFLECT_ONLY",
                sandbox_requirement="NO_SANDBOX",
                max_attempts=1,
                timeout_ms=24 * 60 * 60 * 1000,
                cost_budget=0.0,
                retry_policy="none",
                fallback_policy="abstain_on_timeout",
            ),
        )

    nodes.append(
        WorkflowNode(
            node_id="n_merge_seal",
            node_type=WorkflowNodeType.MERGE_STEP,
            current_ask="Merge branches and seal workflow package",
            required_inputs=("l2_artifact_refs",),
            expected_outputs=("sealed_workflow_package_refs",),
            support_target="NONE",
            capability_requirement="REFLECT_ONLY",
            sandbox_requirement="NO_SANDBOX",
            max_attempts=1,
            timeout_ms=min(workflow_input.route_slo.max_latency_ms, 30_000),
            cost_budget=0.0,
            retry_policy="none",
            fallback_policy="emit_safe_partial",
        ),
    )

    return tuple(nodes)


def _build_edges(nodes: tuple[WorkflowNode, ...]) -> tuple[WorkflowEdge, ...]:
    """Step 5 — build forward-only edges between nodes."""
    edges: list[WorkflowEdge] = []
    ordered_ids = [n.node_id for n in nodes]
    for i, src in enumerate(ordered_ids[:-1]):
        dst = ordered_ids[i + 1]
        edge = WorkflowEdge(
            edge_id=f"e_{src}__{dst}",
            from_node=src,
            to_node=dst,
            dependency_type=EdgeDependencyType.DATA,
            edge_order=i,
            replay_order_key=f"{i:03d}",
        )
        edges.append(edge)
    return tuple(edges)


def build_l3_workflow(workflow_input: L3WorkflowInput) -> ManagedWorkflowBlueprint:
    """Public entrypoint — 03.6 §PHASE 2 DAG BUILDER."""
    if not isinstance(workflow_input, L3WorkflowInput):
        raise L3DoctrineContractError(
            f"workflow_input must be L3WorkflowInput, got {type(workflow_input).__name__}",
        )

    _validate_route_contract_is_managed(workflow_input)
    classification = _classify_execution_shape(workflow_input)
    nodes = _build_nodes(workflow_input, classification)

    if len(nodes) > workflow_input.max_nodes:
        raise L3DoctrineContractError(
            f"Generated node count {len(nodes)} exceeds L3WorkflowInput.max_nodes={workflow_input.max_nodes}",
        )

    edges = _build_edges(nodes)

    blueprint_payload = {
        "route_contract_id": workflow_input.route_contract_id,
        "policy_hash": workflow_input.policy_hash,
        "blueprint_hash": workflow_input.blueprint_hash,
        "nodes": [asdict(n) for n in nodes],
        "edges": [asdict(e) for e in edges],
        "classification_hash": classification.classification_hash,
    }
    graph_hash = _digest(blueprint_payload, "graph")
    workflow_id = _digest({"graph_hash": graph_hash, "route": workflow_input.route_contract_id}, "wf")
    blueprint_id = workflow_input.workflow_blueprint_id or _digest({"graph_hash": graph_hash}, "blueprint")

    dependency_types = tuple({e.dependency_type for e in edges})

    return ManagedWorkflowBlueprint(
        workflow_id=workflow_id,
        route_contract_id=workflow_input.route_contract_id,
        workflow_blueprint_id=blueprint_id,
        nodes=nodes,
        edges=edges,
        dependency_types=dependency_types,
        branch_policy="serial_unless_parallel_safe",
        join_policy="deterministic_order",
        retry_policy="exponential_backoff_capped",
        fallback_policy="cascade_then_r5",
        parallelism_policy=f"max_parallelism={workflow_input.max_parallelism}",
        checkpoint_policy="checkpoint_after_each_node",
        hitl_pause_policy="freeze_packet_then_reclear",
        quality_loop_policy="bounded_iterations",
        evidence_merge_policy="preserve_origin_trust_labels",
        contradiction_policy="flag_do_not_collapse",
        completion_policy="run_completion_test_each_merge",
        replay_metadata=(
            f"policy_hash={workflow_input.policy_hash}",
            f"blueprint_hash={workflow_input.blueprint_hash}",
            f"snapshot_id={workflow_input.snapshot_id}",
            f"route_digest={workflow_input.route_digest}",
        ),
        graph_hash=graph_hash,
    )


__all__ = ["build_l3_workflow"]
