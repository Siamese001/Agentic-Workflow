"""Exhaustive edge-case coverage for L3 doctrine contracts (03.6, 03.7, 03.8).

For every L3 contract type this file verifies type guards, range checks,
NaN rejection, oversize-tuple rejection, must-be-True assertions, entry-law
guards, and DAG laws.

Constitutional compliance: no ``except Exception``, no I/O, no subprocess.
"""

from __future__ import annotations

import math

import pytest

from agentic_core.L3_orchestration.doctrine import L3DoctrineContractError
from agentic_core.L3_orchestration.doctrine.contracts_l3_6 import (
    EdgeDependencyType,
    ExecutionShape,
    ExecutionShapeClassification,
    L3WorkflowInput,
    ManagedWorkflowBlueprint,
    RouteSLOEnvelope,
    WorkflowEdge,
    WorkflowExecutionForm,
    WorkflowNode,
    WorkflowNodeType,
)
from agentic_core.L3_orchestration.doctrine.contracts_l3_7 import (
    CostLatencyObservations,
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
from agentic_core.L3_orchestration.doctrine.contracts_l3_8 import (
    CompletionStatus,
    ConcurrencyPlan,
    CostLatencyTokenSummary,
    FallbackCascadeState,
    QualityLoopPlan,
    SealedWorkflowPackage,
    WorkflowCompletionTest,
    WorkflowOutcomeClass,
)
from agentic_core.L3_orchestration.doctrine.eligibility import build_l3_workflow
from agentic_core.L3_orchestration.doctrine.governance import (
    apply_fallback_control,
    govern_concurrency,
    govern_quality_loop,
    run_completion_test,
    seal_workflow_package,
)
from agentic_core.L3_orchestration.doctrine.state import (
    emit_step_contract,
    ingest_step_result,
    initial_ledger,
    select_next_ready_node,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


_OVERSIZE = "x" * 513


def _valid_slo(**overrides: object) -> RouteSLOEnvelope:
    base: dict[str, object] = dict(
        max_latency_ms=300_000, max_cost=4.0, max_tokens=200_000, max_iterations=4
    )
    base.update(overrides)
    return RouteSLOEnvelope(**base)  # type: ignore[arg-type]


def _valid_workflow_input(**overrides: object) -> L3WorkflowInput:
    base: dict[str, object] = dict(
        route_contract_id="rc",
        selected_route_id="R3R4_MANAGED_WORKFLOW",
        execution_form=WorkflowExecutionForm.MANAGED_WORKFLOW,
        l1_plan_ref="lp",
        task_spec_ref="Audit then propose",
        query_spec_ref="depends on prior step",
        support_expectation="SOURCE_BACKED_SUMMARY",
        action_expectation="multi-step",
        policy_hash="p",
        blueprint_hash="b",
        replay_key="rk",
        snapshot_id="snap",
        route_digest="rd",
        route_slo=_valid_slo(),
        fallback_chain=("R5_FALLBACK",),
        tenant_scope="t",
        acl_scope=("read",),
        capability_class="READ_WRITE",
        sandbox_class="PROCESS_SANDBOX",
    )
    base.update(overrides)
    return L3WorkflowInput(**base)  # type: ignore[arg-type]


def _valid_node(**overrides: object) -> WorkflowNode:
    base: dict[str, object] = dict(
        node_id="n1",
        node_type=WorkflowNodeType.L2_MODEL_STEP,
        current_ask="ask",
        required_inputs=("q",),
        expected_outputs=("a",),
        support_target="SOURCE_BACKED_SUMMARY",
        capability_requirement="READ_WRITE",
        sandbox_requirement="PROCESS_SANDBOX",
        max_attempts=2,
        timeout_ms=30000,
        cost_budget=0.5,
        retry_policy="exponential_backoff",
        fallback_policy="cascade",
    )
    base.update(overrides)
    return WorkflowNode(**base)  # type: ignore[arg-type]


def _valid_edge(**overrides: object) -> WorkflowEdge:
    base: dict[str, object] = dict(
        edge_id="e1",
        from_node="a",
        to_node="b",
        dependency_type=EdgeDependencyType.DATA,
    )
    base.update(overrides)
    return WorkflowEdge(**base)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# 03.6 RouteSLOEnvelope edges
# ---------------------------------------------------------------------------


class TestRouteSLOEnvelopeEdges:

    def test_negative_max_latency_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_slo(max_latency_ms=-1)

    def test_negative_max_tokens_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_slo(max_tokens=-1)

    def test_negative_max_iterations_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_slo(max_iterations=-1)

    def test_max_cost_negative_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_slo(max_cost=-0.1)

    def test_max_cost_nan_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_slo(max_cost=math.nan)

    def test_max_cost_str_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_slo(max_cost="cheap")

    def test_bool_as_int_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_slo(max_latency_ms=True)


# ---------------------------------------------------------------------------
# 03.6 L3WorkflowInput edges
# ---------------------------------------------------------------------------


class TestL3WorkflowInputEdges:

    def test_max_nodes_zero_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_workflow_input(max_nodes=0)

    def test_negative_max_parallelism_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_workflow_input(max_parallelism=-1)

    def test_oversize_fallback_chain_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_workflow_input(fallback_chain=tuple(f"f{i}" for i in range(40)))

    def test_oversize_hitl_pause_points_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_workflow_input(
                hitl_pause_points=tuple(f"p{i}" for i in range(40)),
            )

    def test_wrong_execution_form_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_workflow_input(execution_form="MANAGED_WORKFLOW")  # raw string

    def test_wrong_route_slo_type_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_workflow_input(route_slo="fast")

    @pytest.mark.parametrize(
        "field",
        ["route_contract_id", "policy_hash", "blueprint_hash", "replay_key"],
    )
    def test_empty_required_field_raises(self, field: str) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_workflow_input(**{field: ""})

    def test_oversize_acl_scope_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_workflow_input(acl_scope=tuple(f"acl-{i}" for i in range(300)))

    def test_oversize_route_contract_id_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_workflow_input(route_contract_id=_OVERSIZE)


# ---------------------------------------------------------------------------
# 03.6 ExecutionShapeClassification edges
# ---------------------------------------------------------------------------


def _valid_classification(**overrides: object) -> ExecutionShapeClassification:
    base: dict[str, object] = dict(
        classification_id="cid",
        classification=ExecutionShape.MULTI_STEP_WORKFLOW,
        why_not_single_step=("dependency_chain",),
        why_not_workflow=(),
        changing_step_contracts=(),
        dependency_chain_detected=True,
        branching_detected=False,
        join_detected=False,
        staged_evidence_required=False,
        parallel_shards_detected=False,
        hitl_pause_resume_required=False,
        checkpoint_resume_required=False,
        evaluator_optimizer_loop_required=False,
        ptc_step_candidate_detected=False,
        classification_hash="h",
    )
    base.update(overrides)
    return ExecutionShapeClassification(**base)  # type: ignore[arg-type]


class TestExecutionShapeClassificationEdges:

    def test_multi_step_without_structural_signal_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_classification(
                dependency_chain_detected=False,
                branching_detected=False,
                join_detected=False,
                staged_evidence_required=False,
                parallel_shards_detected=False,
                hitl_pause_resume_required=False,
                checkpoint_resume_required=False,
                evaluator_optimizer_loop_required=False,
            )

    def test_wrong_enum_classification_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_classification(classification="MULTI_STEP_WORKFLOW")

    def test_non_bool_field_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_classification(branching_detected="yes")


# ---------------------------------------------------------------------------
# 03.6 WorkflowNode edges
# ---------------------------------------------------------------------------


class TestWorkflowNodeEdges:

    def test_empty_node_id_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_node(node_id="")

    def test_max_attempts_zero_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_node(max_attempts=0)

    def test_negative_timeout_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_node(timeout_ms=-1)

    def test_cost_budget_negative_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_node(cost_budget=-0.1)

    def test_cost_budget_nan_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_node(cost_budget=math.nan)

    def test_no_direct_execution_assertion_false_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_node(no_direct_execution_assertion=False)

    def test_ptc_on_non_l2_step_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_node(
                node_type=WorkflowNodeType.C0_GROUNDING_STEP,
                ptc_allowed_if_l2_step=True,
            )

    def test_ptc_on_l2_ptc_sandbox_step_validates(self) -> None:
        n = _valid_node(
            node_type=WorkflowNodeType.L2_PTC_SANDBOX_STEP,
            ptc_allowed_if_l2_step=True,
        )
        assert n.ptc_allowed_if_l2_step is True

    def test_wrong_node_type_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_node(node_type="L2_MODEL_STEP")  # raw string

    def test_oversize_required_inputs_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_node(required_inputs=tuple(f"in-{i}" for i in range(300)))


# ---------------------------------------------------------------------------
# 03.6 WorkflowEdge edges
# ---------------------------------------------------------------------------


class TestWorkflowEdgeEdges:

    def test_self_loop_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_edge(from_node="a", to_node="a")

    def test_empty_from_node_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_edge(from_node="")

    def test_empty_edge_id_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_edge(edge_id="")

    def test_wrong_dependency_type_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_edge(dependency_type="DATA")

    def test_negative_edge_order_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_edge(edge_order=-1)


# ---------------------------------------------------------------------------
# 03.6 ManagedWorkflowBlueprint edges
# ---------------------------------------------------------------------------


def _valid_blueprint(**overrides: object) -> ManagedWorkflowBlueprint:
    n1 = _valid_node(node_id="a")
    n2 = _valid_node(node_id="b", node_type=WorkflowNodeType.MERGE_STEP)
    e1 = _valid_edge(edge_id="e_a_b", from_node="a", to_node="b")
    base: dict[str, object] = dict(
        workflow_id="wf",
        route_contract_id="rc",
        workflow_blueprint_id="bp",
        nodes=(n1, n2),
        edges=(e1,),
        branch_policy="serial",
        join_policy="det",
        retry_policy="exp",
        fallback_policy="cascade",
        parallelism_policy="max=4",
        checkpoint_policy="each",
        hitl_pause_policy="freeze",
        quality_loop_policy="bounded",
        evidence_merge_policy="preserve",
        contradiction_policy="flag",
        completion_policy="run_test",
        replay_metadata=(),
        graph_hash="g",
    )
    base.update(overrides)
    return ManagedWorkflowBlueprint(**base)  # type: ignore[arg-type]


class TestManagedWorkflowBlueprintEdges:

    def test_empty_nodes_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_blueprint(nodes=(), edges=())

    def test_duplicate_node_ids_raises(self) -> None:
        n1 = _valid_node(node_id="dup")
        n2 = _valid_node(node_id="dup", node_type=WorkflowNodeType.MERGE_STEP)
        with pytest.raises(L3DoctrineContractError):
            _valid_blueprint(nodes=(n1, n2), edges=())

    def test_edge_referencing_unknown_node_raises(self) -> None:
        n1 = _valid_node(node_id="a")
        bad_edge = _valid_edge(edge_id="e_bad", from_node="a", to_node="ghost")
        with pytest.raises(L3DoctrineContractError):
            _valid_blueprint(nodes=(n1,), edges=(bad_edge,))

    def test_non_node_in_nodes_tuple_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_blueprint(nodes=("not-a-node",), edges=())

    def test_non_edge_in_edges_tuple_raises(self) -> None:
        n1 = _valid_node(node_id="a")
        with pytest.raises(L3DoctrineContractError):
            _valid_blueprint(nodes=(n1,), edges=("not-an-edge",))

    def test_cycle_raises(self) -> None:
        n1 = _valid_node(node_id="a")
        n2 = _valid_node(node_id="b")
        forward = _valid_edge(edge_id="e_ab", from_node="a", to_node="b")
        backward = _valid_edge(edge_id="e_ba", from_node="b", to_node="a")
        with pytest.raises(L3DoctrineContractError):
            _valid_blueprint(nodes=(n1, n2), edges=(forward, backward))


# ---------------------------------------------------------------------------
# 03.7 L3StateLedger edges
# ---------------------------------------------------------------------------


def _valid_ledger(**overrides: object) -> L3StateLedger:
    base: dict[str, object] = dict(
        workflow_id="wf",
        route_contract_id="rc",
        policy_hash="p",
        blueprint_hash="b",
        replay_key="rk",
        graph_hash="g",
        node_states=(("a", NodeState.NOT_READY),),
        edge_states=(),
        branch_states=(),
        join_states=(),
        attempt_counts=(("a", 0),),
        retry_counts=(("a", 0),),
        fallback_depth=0,
        remaining_budget=1.0,
        remaining_slo=1000,
        checkpoints=(),
        paused_packets=(),
        reason_codes=(),
        ledger_hash="h",
    )
    base.update(overrides)
    return L3StateLedger(**base)  # type: ignore[arg-type]


class TestL3StateLedgerEdges:

    def test_negative_fallback_depth_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_ledger(fallback_depth=-1)

    def test_remaining_budget_negative_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_ledger(remaining_budget=-0.1)

    def test_remaining_budget_nan_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_ledger(remaining_budget=math.nan)

    def test_remaining_slo_negative_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_ledger(remaining_slo=-1)

    def test_node_states_wrong_pair_shape_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_ledger(node_states=(("a",),))  # 1-tuple, not pair

    def test_node_states_wrong_state_type_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_ledger(node_states=(("a", "NOT_READY"),))  # raw string

    def test_attempt_counts_negative_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_ledger(attempt_counts=(("a", -1),))

    def test_retry_counts_wrong_shape_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_ledger(retry_counts=(("a", "0"),))  # str count


# ---------------------------------------------------------------------------
# 03.7 NodeReadinessDecision edges
# ---------------------------------------------------------------------------


def _valid_readiness(**overrides: object) -> NodeReadinessDecision:
    base: dict[str, object] = dict(
        decision_id="d",
        workflow_id="w",
        node_id="n",
        ready=True,
        blocked_reasons=(),
        satisfied_dependencies=(),
        unsatisfied_dependencies=(),
        required_evidence_refs=(),
        required_policy_refs=(),
        required_capability_refs=(),
        budget_status="ok",
        retry_status="ok",
        fallback_status="ok",
        hitl_status="none",
        readiness_hash="h",
    )
    base.update(overrides)
    return NodeReadinessDecision(**base)  # type: ignore[arg-type]


class TestNodeReadinessDecisionEdges:

    def test_ready_true_with_blocked_reasons_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_readiness(blocked_reasons=("dep_unsatisfied",))

    def test_non_bool_ready_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_readiness(ready="yes")


# ---------------------------------------------------------------------------
# 03.7 L3StepContract edges
# ---------------------------------------------------------------------------


def _valid_step(**overrides: object) -> L3StepContract:
    base: dict[str, object] = dict(
        step_contract_id="sc",
        workflow_id="w",
        node_id="n",
        attempt_id="a1",
        parent_route_id="R3R4_MANAGED_WORKFLOW",
        route_digest="rd",
        policy_hash="p",
        blueprint_hash="b",
        snapshot_id="snap",
        replay_key="rk",
        idempotency_key="idem",
        node_type=WorkflowNodeType.L2_MODEL_STEP,
        current_work_order="do",
        inputs=StepInputs(),
        expected_output_contract="SealedL2Artifact",
        capability_token_requirement="READ_WRITE",
        sandbox_envelope_requirement="PROCESS_SANDBOX",
        timeout_ms=30000,
        retry_policy="exp",
        fallback_permission="cascade",
        telemetry_keys=(),
        expected_receipts=(),
        step_contract_hash="h",
    )
    base.update(overrides)
    return L3StepContract(**base)  # type: ignore[arg-type]


class TestL3StepContractEdges:

    def test_no_durable_commit_authority_false_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_step(no_durable_commit_authority=False)

    def test_timeout_zero_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_step(timeout_ms=0)

    def test_negative_timeout_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_step(timeout_ms=-1)

    def test_inputs_wrong_type_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_step(inputs="not-inputs")

    def test_node_type_wrong_enum_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_step(node_type="L2_MODEL_STEP")


# ---------------------------------------------------------------------------
# 03.7 StepResultIngest + CostLatencyObservations edges
# ---------------------------------------------------------------------------


def _valid_obs(**overrides: object) -> CostLatencyObservations:
    base: dict[str, object] = dict(
        latency_ms=100, tokens=200, cost=0.01, quality_score=0.9
    )
    base.update(overrides)
    return CostLatencyObservations(**base)  # type: ignore[arg-type]


class TestCostLatencyObservationsEdges:

    def test_negative_latency_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_obs(latency_ms=-1)

    def test_quality_score_above_one_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_obs(quality_score=1.5)

    def test_quality_score_nan_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_obs(quality_score=math.nan)

    def test_cost_negative_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_obs(cost=-0.01)

    def test_cost_str_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_obs(cost="cheap")


def _valid_step_result(**overrides: object) -> StepResultIngest:
    base: dict[str, object] = dict(
        step_contract_id="sc",
        sealed_l2_artifact_ref="art",
        status=StepResultStatus.SUCCESS,
        output_artifact_refs=(),
        proposed_state_diff_refs=(),
        returned_evidence_refs=(),
        returned_graph_refs=(),
        retry_signal="",
        branch_result="",
        handoff_signal="",
        needs_help_signal="",
        hitl_pause_signal="",
        cost_latency_observations=_valid_obs(),
        replay_receipt_refs=(),
        ingest_hash="h",
    )
    base.update(overrides)
    return StepResultIngest(**base)  # type: ignore[arg-type]


class TestStepResultIngestEdges:

    def test_quality_signal_above_one_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_step_result(quality_signal=1.5)

    def test_quality_signal_nan_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_step_result(quality_signal=math.nan)

    def test_status_wrong_enum_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_step_result(status="SUCCESS")

    def test_observations_wrong_type_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_step_result(cost_latency_observations="fast")


# ---------------------------------------------------------------------------
# 03.7 HandoffMergeReceipt edges
# ---------------------------------------------------------------------------


class TestHandoffMergeReceiptEdges:

    def test_durable_write_attempted_true_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            HandoffMergeReceipt(
                receipt_id="r",
                workflow_id="w",
                node_id="n",
                new_state=NodeState.SUCCEEDED,
                reason_codes=("ok",),
                preserved_lineage_refs=(),
                contradiction_flags=(),
                durable_write_attempted=True,
            )

    def test_wrong_state_enum_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            HandoffMergeReceipt(
                receipt_id="r",
                workflow_id="w",
                node_id="n",
                new_state="SUCCEEDED",
                reason_codes=("ok",),
                preserved_lineage_refs=(),
                contradiction_flags=(),
            )


# ---------------------------------------------------------------------------
# 03.7 state.py public API edges
# ---------------------------------------------------------------------------


class TestStatePublicAPIEdges:

    def test_select_next_ready_node_wrong_ledger_raises(self) -> None:
        bp = build_l3_workflow(_valid_workflow_input())
        bus = L3ContextBus(workflow_id=bp.workflow_id, bus_hash="h")
        with pytest.raises(L3DoctrineContractError):
            select_next_ready_node("not-a-ledger", bp, bus)  # type: ignore[arg-type]

    def test_select_next_ready_node_wrong_blueprint_raises(self) -> None:
        bp = build_l3_workflow(_valid_workflow_input())
        ledger = initial_ledger(
            bp,
            policy_hash="p",
            blueprint_hash="b",
            replay_key="rk",
            route_contract_id="rc",
            initial_budget=10.0,
            initial_slo_ms=300_000,
        )
        bus = L3ContextBus(workflow_id=bp.workflow_id, bus_hash="h")
        with pytest.raises(L3DoctrineContractError):
            select_next_ready_node(ledger, "not-a-blueprint", bus)  # type: ignore[arg-type]

    def test_select_next_ready_node_wrong_bus_raises(self) -> None:
        bp = build_l3_workflow(_valid_workflow_input())
        ledger = initial_ledger(
            bp,
            policy_hash="p",
            blueprint_hash="b",
            replay_key="rk",
            route_contract_id="rc",
            initial_budget=10.0,
            initial_slo_ms=300_000,
        )
        with pytest.raises(L3DoctrineContractError):
            select_next_ready_node(ledger, bp, "not-a-bus")  # type: ignore[arg-type]

    def test_emit_step_contract_wrong_decision_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            emit_step_contract(
                "not-a-decision",  # type: ignore[arg-type]
                None,  # type: ignore[arg-type]
                None,  # type: ignore[arg-type]
                None,  # type: ignore[arg-type]
                parent_route_id="x",
                route_digest="x",
                snapshot_id="x",
            )

    def test_ingest_step_result_wrong_input_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            ingest_step_result("not-a-result", workflow_id="w", node_id="n")  # type: ignore[arg-type]

    def test_ingest_step_result_empty_node_id_raises(self) -> None:
        sr = _valid_step_result()
        with pytest.raises(L3DoctrineContractError):
            ingest_step_result(sr, workflow_id="w", node_id="")

    def test_initial_ledger_wrong_blueprint_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            initial_ledger(
                "not-a-blueprint",  # type: ignore[arg-type]
                policy_hash="p",
                blueprint_hash="b",
                replay_key="rk",
                route_contract_id="rc",
                initial_budget=1.0,
                initial_slo_ms=1000,
            )

    def test_initial_ledger_negative_budget_raises(self) -> None:
        bp = build_l3_workflow(_valid_workflow_input())
        with pytest.raises(L3DoctrineContractError):
            initial_ledger(
                bp,
                policy_hash="p",
                blueprint_hash="b",
                replay_key="rk",
                route_contract_id="rc",
                initial_budget=-1.0,
                initial_slo_ms=1000,
            )

    def test_initial_ledger_negative_slo_raises(self) -> None:
        bp = build_l3_workflow(_valid_workflow_input())
        with pytest.raises(L3DoctrineContractError):
            initial_ledger(
                bp,
                policy_hash="p",
                blueprint_hash="b",
                replay_key="rk",
                route_contract_id="rc",
                initial_budget=1.0,
                initial_slo_ms=-1,
            )


# ---------------------------------------------------------------------------
# 03.7 select_next_ready_node behavior edges
# ---------------------------------------------------------------------------


class TestSelectNextReadyNodeBehaviorEdges:

    def test_paused_hitl_node_skipped(self) -> None:
        bp = build_l3_workflow(_valid_workflow_input())
        first_id = bp.nodes[0].node_id
        # Mark first node PAUSED_HITL — it should be skipped
        states = []
        for n in bp.nodes:
            if n.node_id == first_id:
                states.append((n.node_id, NodeState.PAUSED_HITL))
            else:
                states.append((n.node_id, NodeState.NOT_READY))
        states_sorted = tuple(sorted(states, key=lambda p: p[0]))
        ledger = _valid_ledger(
            workflow_id=bp.workflow_id,
            graph_hash=bp.graph_hash,
            node_states=states_sorted,
            attempt_counts=tuple(sorted(((n.node_id, 0) for n in bp.nodes), key=lambda p: p[0])),
            retry_counts=tuple(sorted(((n.node_id, 0) for n in bp.nodes), key=lambda p: p[0])),
            remaining_budget=10.0,
            remaining_slo=300_000,
        )
        bus = L3ContextBus(workflow_id=bp.workflow_id, bus_hash="h")
        decision = select_next_ready_node(ledger, bp, bus)
        # Skipped first node → next eligible node is considered (its deps may or may not satisfy)
        assert decision.node_id != first_id


# ---------------------------------------------------------------------------
# 03.8 ConcurrencyPlan + governors edges
# ---------------------------------------------------------------------------


class TestGovernConcurrencyEdges:

    def test_max_parallelism_zero_raises(self) -> None:
        bp = build_l3_workflow(_valid_workflow_input())
        ledger = initial_ledger(
            bp,
            policy_hash="p",
            blueprint_hash="b",
            replay_key="rk",
            route_contract_id="rc",
            initial_budget=10.0,
            initial_slo_ms=300_000,
        )
        with pytest.raises(L3DoctrineContractError):
            govern_concurrency(ledger, bp, max_parallelism=0)

    def test_resource_ceiling_zero_raises(self) -> None:
        bp = build_l3_workflow(_valid_workflow_input())
        ledger = initial_ledger(
            bp,
            policy_hash="p",
            blueprint_hash="b",
            replay_key="rk",
            route_contract_id="rc",
            initial_budget=10.0,
            initial_slo_ms=300_000,
        )
        with pytest.raises(L3DoctrineContractError):
            govern_concurrency(ledger, bp, resource_ceiling=0)

    def test_wrong_ledger_type_raises(self) -> None:
        bp = build_l3_workflow(_valid_workflow_input())
        with pytest.raises(L3DoctrineContractError):
            govern_concurrency("not-a-ledger", bp)  # type: ignore[arg-type]


def _valid_concurrency(**overrides: object) -> ConcurrencyPlan:
    base: dict[str, object] = dict(
        workflow_id="w",
        parallel_groups=(("a",),),
        serial_only_nodes=("a",),
        max_parallelism=4,
        branch_policy="serial",
        join_policy="det",
        race_prevention_policy="lock",
        shard_failure_policy="partial",
        deterministic_join_order=("a",),
        resource_ceiling=16,
        concurrency_plan_hash="h",
    )
    base.update(overrides)
    return ConcurrencyPlan(**base)  # type: ignore[arg-type]


class TestConcurrencyPlanEdges:

    def test_negative_max_parallelism_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_concurrency(max_parallelism=-1)

    def test_non_tuple_parallel_groups_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_concurrency(parallel_groups=[("a",)])  # list, not tuple

    def test_inner_group_non_tuple_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_concurrency(parallel_groups=(["a"],))


# ---------------------------------------------------------------------------
# 03.8 QualityLoopPlan + governor edges
# ---------------------------------------------------------------------------


def _valid_quality_plan(**overrides: object) -> QualityLoopPlan:
    base: dict[str, object] = dict(
        workflow_id="w",
        loop_id="loop-1",
        evaluator_node_refs=(),
        optimizer_node_refs=(),
        quality_threshold=0.85,
        max_iterations=4,
        diminishing_returns_policy="x",
        oscillation_detection_policy="x",
        best_artifact_retention_policy="x",
        budget_stop_policy="x",
        quality_loop_hash="h",
    )
    base.update(overrides)
    return QualityLoopPlan(**base)  # type: ignore[arg-type]


class TestQualityLoopPlanEdges:

    def test_max_iterations_zero_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_quality_plan(max_iterations=0)

    def test_quality_threshold_above_one_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_quality_plan(quality_threshold=1.2)

    def test_quality_threshold_nan_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_quality_plan(quality_threshold=math.nan)


class TestGovernQualityLoopEdges:

    def test_wrong_plan_type_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            govern_quality_loop("not-plan", current_score=0.5, current_iteration=1)  # type: ignore[arg-type]

    def test_current_score_above_one_raises(self) -> None:
        plan = _valid_quality_plan()
        with pytest.raises(L3DoctrineContractError):
            govern_quality_loop(plan, current_score=1.2, current_iteration=1)

    def test_current_score_nan_raises(self) -> None:
        plan = _valid_quality_plan()
        with pytest.raises(L3DoctrineContractError):
            govern_quality_loop(plan, current_score=math.nan, current_iteration=1)

    def test_negative_current_iteration_raises(self) -> None:
        plan = _valid_quality_plan()
        with pytest.raises(L3DoctrineContractError):
            govern_quality_loop(plan, current_score=0.5, current_iteration=-1)

    def test_budget_exhausted_stops(self) -> None:
        plan = _valid_quality_plan(quality_threshold=0.99, max_iterations=10)
        receipt = govern_quality_loop(
            plan, current_score=0.5, current_iteration=1, remaining_budget=0.0
        )
        assert receipt.stop is True
        assert receipt.reason == "budget_exhausted"

    def test_oscillation_stops(self) -> None:
        plan = _valid_quality_plan(quality_threshold=0.99, max_iterations=10)
        receipt = govern_quality_loop(
            plan, current_score=0.5, current_iteration=1, last_score=0.505
        )
        assert receipt.stop is True
        assert "oscillation" in receipt.reason or "no_material_improvement" in receipt.reason


# ---------------------------------------------------------------------------
# 03.8 FallbackCascadeState + apply_fallback_control edges
# ---------------------------------------------------------------------------


def _valid_fallback_state(**overrides: object) -> FallbackCascadeState:
    base: dict[str, object] = dict(
        workflow_id="w",
        fallback_chain=("R5_FALLBACK",),
        fallback_depth=0,
        attempted_fallbacks=(),
        current_fallback_candidate="",
        fallback_reason_codes=(),
        provider_tool_alternatives=(),
        tier_cascade_state="initial",
        circuit_breaker_status="closed",
        fallback_hash="h",
    )
    base.update(overrides)
    return FallbackCascadeState(**base)  # type: ignore[arg-type]


class TestFallbackCascadeStateEdges:

    def test_no_silent_fallback_assertion_false_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_fallback_state(no_silent_fallback_assertion=False)

    def test_attempted_without_reasons_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_fallback_state(
                attempted_fallbacks=("R5_FALLBACK",),
                fallback_reason_codes=(),
            )

    def test_negative_fallback_depth_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_fallback_state(fallback_depth=-1)


class TestApplyFallbackControlEdges:

    def test_wrong_state_type_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            apply_fallback_control(
                "not-state", next_candidate="R5_FALLBACK", reason_code="r"  # type: ignore[arg-type]
            )

    def test_empty_next_candidate_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            apply_fallback_control(
                _valid_fallback_state(), next_candidate="", reason_code="r"
            )

    def test_empty_reason_code_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            apply_fallback_control(
                _valid_fallback_state(),
                next_candidate="R5_FALLBACK",
                reason_code="",
            )


# ---------------------------------------------------------------------------
# 03.8 WorkflowCompletionTest edges
# ---------------------------------------------------------------------------


def _valid_completion(**overrides: object) -> WorkflowCompletionTest:
    base: dict[str, object] = dict(
        workflow_id="w",
        all_required_nodes_sealed=True,
        mandatory_branches_resolved=True,
        joins_complete=True,
        required_support_satisfied=True,
        contradictions_labeled=False,
        unresolved_gaps_carried_forward=False,
        route_success_conditions_satisfied=True,
        mutation_proposal_only=True,
        hitl_pause_resolved_or_carried=True,
        budget_status="ok",
        best_partial_available=False,
        completion_status=CompletionStatus.COMPLETE,
        completion_hash="h",
    )
    base.update(overrides)
    return WorkflowCompletionTest(**base)  # type: ignore[arg-type]


class TestWorkflowCompletionTestEdges:

    def test_mutation_proposal_only_false_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_completion(mutation_proposal_only=False)

    @pytest.mark.parametrize(
        "field",
        [
            "all_required_nodes_sealed",
            "mandatory_branches_resolved",
            "joins_complete",
            "required_support_satisfied",
            "route_success_conditions_satisfied",
        ],
    )
    def test_complete_without_invariant_raises(self, field: str) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_completion(**{field: False})

    def test_completion_status_wrong_enum_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_completion(completion_status="COMPLETE")


# ---------------------------------------------------------------------------
# 03.8 SealedWorkflowPackage edges
# ---------------------------------------------------------------------------


def _valid_package(**overrides: object) -> SealedWorkflowPackage:
    base: dict[str, object] = dict(
        sealed_workflow_package_id="pkg",
        workflow_id="w",
        route_contract_id="rc",
        request_id="r",
        run_id="rn",
        trace_root="tr",
        policy_hash="p",
        blueprint_hash="b",
        replay_key="rk",
        graph_hash="g",
        ledger_hash="l",
        completed_node_refs=(),
        sealed_l2_artifact_refs=(),
        prompt_artifact_refs=(),
        evidence_contract_refs=(),
        branch_join_manifest="default",
        fallback_manifest="default",
        quality_loop_manifest="default",
        contradiction_flags=(),
        unresolved_gaps=(),
        best_partial_artifact_refs=(),
        proposed_state_diff_refs=(),
        hitl_packet_refs=(),
        cost_latency_token_summary=CostLatencyTokenSummary(),
        workflow_outcome_class=WorkflowOutcomeClass.CLEAN,
        route_success_condition_status="satisfied",
        package_hash="h",
    )
    base.update(overrides)
    return SealedWorkflowPackage(**base)  # type: ignore[arg-type]


class TestSealedWorkflowPackageEdges:

    @pytest.mark.parametrize(
        "field",
        [
            "mutation_proposal_only_assertion",
            "exit_review_required",
            "no_durable_commit_assertion",
        ],
    )
    def test_assertion_false_raises(self, field: str) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_package(**{field: False})

    def test_outcome_class_wrong_enum_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_package(workflow_outcome_class="CLEAN")

    def test_cost_summary_wrong_type_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_package(cost_latency_token_summary="fast")


class TestCostLatencyTokenSummaryEdges:

    def test_negative_total_cost_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            CostLatencyTokenSummary(total_cost=-0.01)

    def test_total_cost_nan_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            CostLatencyTokenSummary(total_cost=math.nan)

    def test_negative_latency_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            CostLatencyTokenSummary(total_latency_ms=-1)


# ---------------------------------------------------------------------------
# 03.8 seal_workflow_package edges
# ---------------------------------------------------------------------------


class TestSealWorkflowPackageEdges:

    def _make_state(self) -> tuple:
        bp = build_l3_workflow(_valid_workflow_input())
        bus = L3ContextBus(
            workflow_id=bp.workflow_id,
            bus_hash="h",
            carried_l2_artifact_refs=("art",),
        )
        ledger = initial_ledger(
            bp,
            policy_hash="p",
            blueprint_hash="b",
            replay_key="rk",
            route_contract_id="rc",
            initial_budget=10.0,
            initial_slo_ms=300_000,
        )
        return bp, bus, ledger

    def test_seal_refused_for_needs_hitl_pause(self) -> None:
        bp, bus, ledger = self._make_state()
        # Force NEEDS_HITL_PAUSE by leaving a node PAUSED_HITL
        bad_states = []
        for i, n in enumerate(bp.nodes):
            bad_states.append((n.node_id, NodeState.PAUSED_HITL if i == 0 else NodeState.SUCCEEDED))
        bad_ledger = _valid_ledger(
            workflow_id=bp.workflow_id,
            graph_hash=bp.graph_hash,
            node_states=tuple(sorted(bad_states, key=lambda p: p[0])),
            attempt_counts=tuple(sorted(((n.node_id, 0) for n in bp.nodes), key=lambda p: p[0])),
            retry_counts=tuple(sorted(((n.node_id, 0) for n in bp.nodes), key=lambda p: p[0])),
            remaining_budget=ledger.remaining_budget,
            remaining_slo=ledger.remaining_slo,
        )
        completion = run_completion_test(bad_ledger, bp, bus)
        assert completion.completion_status == CompletionStatus.NEEDS_HITL_PAUSE
        with pytest.raises(L3DoctrineContractError):
            seal_workflow_package(
                ledger=bad_ledger,
                blueprint=bp,
                context_bus=bus,
                completion=completion,
                request_id="r",
                run_id="rn",
                trace_root="tr",
                cost_summary=CostLatencyTokenSummary(),
            )


# ---------------------------------------------------------------------------
# 03.6 build_l3_workflow public-API edges
# ---------------------------------------------------------------------------


class TestBuildL3WorkflowAPIEdges:

    def test_wrong_input_type_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            build_l3_workflow("not-an-input")  # type: ignore[arg-type]

    def test_missing_policy_hash_at_step1_raises(self) -> None:
        # Policy_hash is required at construction; removing tests entry-law on the validator.
        with pytest.raises(L3DoctrineContractError):
            _valid_workflow_input(policy_hash="")
