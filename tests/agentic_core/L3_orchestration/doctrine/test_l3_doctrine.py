"""Unit tests for the 03.6/03.7/03.8 L3 doctrine contracts and pipeline.

Constitutional compliance:

- No ``pytest.mark.skip`` (constitutional §1).
- No bare ``except Exception`` (constitutional §15).
"""

from __future__ import annotations

import pytest

from agentic_core.L3_orchestration.doctrine import L3DoctrineContractError
from agentic_core.L3_orchestration.doctrine.contracts_l3_6 import (
    EdgeDependencyType,
    ExecutionShape,
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
    NodeReadinessDecision,
    NodeState,
    StepResultIngest,
    StepResultStatus,
)
from agentic_core.L3_orchestration.doctrine.contracts_l3_8 import (
    CompletionStatus,
    CostLatencyTokenSummary,
    FallbackCascadeState,
    QualityLoopPlan,
    SealedWorkflowPackage,
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


def _valid_workflow_input(**overrides: object) -> L3WorkflowInput:
    base: dict[str, object] = dict(
        route_contract_id="rc-1",
        selected_route_id="R3R4_MANAGED_WORKFLOW",
        execution_form=WorkflowExecutionForm.MANAGED_WORKFLOW,
        l1_plan_ref="lp-1",
        task_spec_ref="Audit repo for X then propose migration plan",
        query_spec_ref="depends on prior step",
        support_expectation="SOURCE_BACKED_SUMMARY",
        action_expectation="multi-step propose",
        policy_hash="p",
        blueprint_hash="b",
        replay_key="rk",
        snapshot_id="snap",
        route_digest="rd",
        route_slo=RouteSLOEnvelope(
            max_latency_ms=300_000,
            max_cost=4.0,
            max_tokens=200_000,
            max_iterations=4,
        ),
        fallback_chain=("R3R4_MANAGED_WORKFLOW", "R5_FALLBACK"),
        tenant_scope="t",
        acl_scope=("read",),
        capability_class="READ_WRITE",
        sandbox_class="PROCESS_SANDBOX",
    )
    base.update(overrides)
    return L3WorkflowInput(**base)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# 03.6 eligibility + DAG
# ---------------------------------------------------------------------------


class TestL36Eligibility:
    def test_l3_refuses_non_managed_workflow(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_workflow_input(selected_route_id="R3_SIMPLE_GROUNDED_READ")

    def test_build_l3_workflow_emits_blueprint(self) -> None:
        bp = build_l3_workflow(_valid_workflow_input())
        assert isinstance(bp, ManagedWorkflowBlueprint)
        assert len(bp.nodes) > 0
        assert len(bp.edges) >= len(bp.nodes) - 1
        assert bp.graph_hash.startswith("graph:")

    def test_dag_has_no_backward_edges(self) -> None:
        bp = build_l3_workflow(_valid_workflow_input())
        # Construct a copy with a backward edge — should fail.
        forward_edge = bp.edges[0]
        backward = WorkflowEdge(
            edge_id="e_backward",
            from_node=forward_edge.to_node,
            to_node=forward_edge.from_node,
            dependency_type=EdgeDependencyType.DATA,
        )
        with pytest.raises(L3DoctrineContractError):
            ManagedWorkflowBlueprint(
                workflow_id=bp.workflow_id,
                route_contract_id=bp.route_contract_id,
                workflow_blueprint_id=bp.workflow_blueprint_id,
                nodes=bp.nodes,
                edges=bp.edges + (backward,),
                branch_policy=bp.branch_policy,
                join_policy=bp.join_policy,
                retry_policy=bp.retry_policy,
                fallback_policy=bp.fallback_policy,
                parallelism_policy=bp.parallelism_policy,
                checkpoint_policy=bp.checkpoint_policy,
                hitl_pause_policy=bp.hitl_pause_policy,
                quality_loop_policy=bp.quality_loop_policy,
                evidence_merge_policy=bp.evidence_merge_policy,
                contradiction_policy=bp.contradiction_policy,
                completion_policy=bp.completion_policy,
                replay_metadata=bp.replay_metadata,
                graph_hash=bp.graph_hash,
            )

    def test_max_iterations_zero_fails_closed(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _valid_workflow_input(max_iterations=0)

    def test_workflow_node_unique_ids(self) -> None:
        bp = build_l3_workflow(_valid_workflow_input())
        ids = [n.node_id for n in bp.nodes]
        assert len(ids) == len(set(ids))

    def test_simple_task_classification(self) -> None:
        # Single-step phrasing -> DIRECT_STEP_PACKAGE shape from classifier
        # (build_l3_workflow still returns a blueprint shell).
        bp = build_l3_workflow(
            _valid_workflow_input(
                task_spec_ref="What is X?",
                query_spec_ref="X definition",
                action_expectation="",
            ),
        )
        assert isinstance(bp, ManagedWorkflowBlueprint)


# ---------------------------------------------------------------------------
# 03.7 state ledger + step contract
# ---------------------------------------------------------------------------


class TestL37State:
    def _setup(self) -> tuple[ManagedWorkflowBlueprint, L3ContextBus]:
        bp = build_l3_workflow(_valid_workflow_input())
        bus = L3ContextBus(
            workflow_id=bp.workflow_id,
            bus_hash="bus-1",
            carried_query_refs=("q-1",),
        )
        return bp, bus

    def test_initial_ledger_marks_all_not_ready(self) -> None:
        bp, _ = self._setup()
        ledger = initial_ledger(
            bp,
            policy_hash="p",
            blueprint_hash="b",
            replay_key="rk",
            route_contract_id="rc",
            initial_budget=10.0,
            initial_slo_ms=300_000,
        )
        for _, state in ledger.node_states:
            assert state == NodeState.NOT_READY

    def test_select_first_ready_returns_first_node(self) -> None:
        bp, bus = self._setup()
        ledger = initial_ledger(
            bp,
            policy_hash="p",
            blueprint_hash="b",
            replay_key="rk",
            route_contract_id="rc",
            initial_budget=10.0,
            initial_slo_ms=300_000,
        )
        decision = select_next_ready_node(ledger, bp, bus)
        assert isinstance(decision, NodeReadinessDecision)
        # First node has no incoming edges -> ready.
        assert decision.ready is True
        assert decision.node_id == bp.nodes[0].node_id

    def test_emit_step_contract_refuses_when_not_ready(self) -> None:
        bp, bus = self._setup()
        ledger = initial_ledger(
            bp,
            policy_hash="p",
            blueprint_hash="b",
            replay_key="rk",
            route_contract_id="rc",
            initial_budget=0.0,  # exhausted
            initial_slo_ms=0,
        )
        decision = select_next_ready_node(ledger, bp, bus)
        # Decision is not ready due to budget.
        assert decision.ready is False
        with pytest.raises(L3DoctrineContractError):
            emit_step_contract(
                decision,
                ledger,
                bp,
                bus,
                parent_route_id="R3R4_MANAGED_WORKFLOW",
                route_digest="rd",
                snapshot_id="snap",
            )

    def test_emit_step_contract_returns_bounded_step(self) -> None:
        bp, bus = self._setup()
        ledger = initial_ledger(
            bp,
            policy_hash="p",
            blueprint_hash="b",
            replay_key="rk",
            route_contract_id="rc",
            initial_budget=10.0,
            initial_slo_ms=300_000,
        )
        decision = select_next_ready_node(ledger, bp, bus)
        contract = emit_step_contract(
            decision,
            ledger,
            bp,
            bus,
            parent_route_id="R3R4_MANAGED_WORKFLOW",
            route_digest="rd",
            snapshot_id="snap",
        )
        assert contract.no_durable_commit_authority is True
        assert contract.workflow_id == ledger.workflow_id
        assert contract.node_id == bp.nodes[0].node_id

    def test_ingest_step_result_returns_merge_receipt(self) -> None:
        bp, _ = self._setup()
        sr = StepResultIngest(
            step_contract_id="step-1",
            sealed_l2_artifact_ref="art-1",
            status=StepResultStatus.SUCCESS,
            output_artifact_refs=("out-1",),
            proposed_state_diff_refs=tuple(),
            returned_evidence_refs=("ev-1",),
            returned_graph_refs=tuple(),
            retry_signal="",
            branch_result="",
            handoff_signal="",
            needs_help_signal="",
            hitl_pause_signal="",
            cost_latency_observations=CostLatencyObservations(
                latency_ms=100, tokens=200, cost=0.01, quality_score=0.9
            ),
            replay_receipt_refs=("rcpt",),
            ingest_hash="ih",
            quality_signal=0.9,
        )
        rcpt = ingest_step_result(sr, workflow_id=bp.workflow_id, node_id=bp.nodes[0].node_id)
        assert isinstance(rcpt, HandoffMergeReceipt)
        assert rcpt.new_state == NodeState.SUCCEEDED
        assert rcpt.durable_write_attempted is False


# ---------------------------------------------------------------------------
# 03.8 governance
# ---------------------------------------------------------------------------


class TestL38Governance:
    def _ledger_and_bp(self) -> tuple:
        bp = build_l3_workflow(_valid_workflow_input())
        bus = L3ContextBus(
            workflow_id=bp.workflow_id,
            bus_hash="bus",
            carried_l2_artifact_refs=("art-1",),
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
        # Mark all nodes SUCCEEDED so we can complete the workflow.
        from agentic_core.L3_orchestration.doctrine.contracts_l3_7 import L3StateLedger

        succeeded = tuple(sorted(((n.node_id, NodeState.SUCCEEDED) for n in bp.nodes), key=lambda p: p[0]))
        ledger = L3StateLedger(
            workflow_id=ledger.workflow_id,
            route_contract_id=ledger.route_contract_id,
            policy_hash=ledger.policy_hash,
            blueprint_hash=ledger.blueprint_hash,
            replay_key=ledger.replay_key,
            graph_hash=ledger.graph_hash,
            node_states=succeeded,
            edge_states=ledger.edge_states,
            branch_states=ledger.branch_states,
            join_states=ledger.join_states,
            attempt_counts=ledger.attempt_counts,
            retry_counts=ledger.retry_counts,
            fallback_depth=0,
            remaining_budget=ledger.remaining_budget,
            remaining_slo=ledger.remaining_slo,
            checkpoints=ledger.checkpoints,
            paused_packets=ledger.paused_packets,
            reason_codes=ledger.reason_codes,
            ledger_hash=ledger.ledger_hash,
        )
        return bp, bus, ledger

    def test_govern_concurrency_returns_serial_plan(self) -> None:
        bp, _, ledger = self._ledger_and_bp()
        plan = govern_concurrency(ledger, bp, max_parallelism=4, resource_ceiling=16)
        assert plan.max_parallelism == 4
        assert plan.workflow_id == ledger.workflow_id
        assert plan.deterministic_join_order != ()

    def test_govern_quality_loop_stops_on_threshold(self) -> None:
        plan = QualityLoopPlan(
            workflow_id="w",
            loop_id="loop-1",
            evaluator_node_refs=("n-1",),
            optimizer_node_refs=("n-2",),
            quality_threshold=0.8,
            max_iterations=4,
            diminishing_returns_policy="stop",
            oscillation_detection_policy="stop",
            best_artifact_retention_policy="keep_best",
            budget_stop_policy="hard",
            quality_loop_hash="h",
        )
        receipt = govern_quality_loop(
            plan,
            current_score=0.85,
            current_iteration=1,
        )
        assert receipt.stop is True
        assert "threshold_reached" in receipt.reason

    def test_govern_quality_loop_stops_on_max_iter(self) -> None:
        plan = QualityLoopPlan(
            workflow_id="w",
            loop_id="loop-1",
            evaluator_node_refs=(),
            optimizer_node_refs=(),
            quality_threshold=0.95,
            max_iterations=2,
            diminishing_returns_policy="x",
            oscillation_detection_policy="x",
            best_artifact_retention_policy="x",
            budget_stop_policy="x",
            quality_loop_hash="h",
        )
        receipt = govern_quality_loop(plan, current_score=0.5, current_iteration=2)
        assert receipt.stop is True

    def test_apply_fallback_control_advances_state(self) -> None:
        state = FallbackCascadeState(
            workflow_id="w",
            fallback_chain=("R5_FALLBACK",),
            fallback_depth=0,
            attempted_fallbacks=tuple(),
            current_fallback_candidate="",
            fallback_reason_codes=tuple(),
            provider_tool_alternatives=tuple(),
            tier_cascade_state="initial",
            circuit_breaker_status="closed",
            fallback_hash="h-init",
        )
        new_state = apply_fallback_control(
            state,
            next_candidate="R5_FALLBACK",
            reason_code="PROVIDER_OUTAGE",
        )
        assert new_state.fallback_depth == 1
        assert "R5_FALLBACK" in new_state.attempted_fallbacks
        assert "PROVIDER_OUTAGE" in new_state.fallback_reason_codes

    def test_apply_fallback_control_rejects_off_chain_candidate(self) -> None:
        state = FallbackCascadeState(
            workflow_id="w",
            fallback_chain=("R5_FALLBACK",),
            fallback_depth=0,
            attempted_fallbacks=tuple(),
            current_fallback_candidate="",
            fallback_reason_codes=tuple(),
            provider_tool_alternatives=tuple(),
            tier_cascade_state="initial",
            circuit_breaker_status="closed",
            fallback_hash="h-init",
        )
        with pytest.raises(L3DoctrineContractError):
            apply_fallback_control(state, next_candidate="R3_SIMPLE_GROUNDED_READ", reason_code="x")

    def test_run_completion_test_returns_complete(self) -> None:
        bp, bus, ledger = self._ledger_and_bp()
        result = run_completion_test(ledger, bp, bus)
        assert result.completion_status == CompletionStatus.COMPLETE
        assert result.mutation_proposal_only is True

    def test_seal_workflow_package_returns_pkg(self) -> None:
        bp, bus, ledger = self._ledger_and_bp()
        completion = run_completion_test(ledger, bp, bus)
        pkg = seal_workflow_package(
            ledger=ledger,
            blueprint=bp,
            context_bus=bus,
            completion=completion,
            request_id="r",
            run_id="rn",
            trace_root="tr",
            cost_summary=CostLatencyTokenSummary(total_latency_ms=1000, total_tokens=2000, total_cost=0.05),
        )
        assert isinstance(pkg, SealedWorkflowPackage)
        assert pkg.workflow_outcome_class == WorkflowOutcomeClass.CLEAN
        assert pkg.exit_review_required is True
        assert pkg.no_durable_commit_assertion is True

    def test_seal_workflow_package_refuses_unsealable(self) -> None:
        bp, bus, ledger = self._ledger_and_bp()
        # Force NEEDS_NEXT_NODE by leaving a node NOT_READY.
        from agentic_core.L3_orchestration.doctrine.contracts_l3_7 import L3StateLedger

        bad = L3StateLedger(
            workflow_id=ledger.workflow_id,
            route_contract_id=ledger.route_contract_id,
            policy_hash=ledger.policy_hash,
            blueprint_hash=ledger.blueprint_hash,
            replay_key=ledger.replay_key,
            graph_hash=ledger.graph_hash,
            node_states=tuple(
                sorted(((n.node_id, NodeState.NOT_READY) for n in bp.nodes), key=lambda p: p[0])
            ),
            edge_states=ledger.edge_states,
            branch_states=ledger.branch_states,
            join_states=ledger.join_states,
            attempt_counts=ledger.attempt_counts,
            retry_counts=ledger.retry_counts,
            fallback_depth=0,
            remaining_budget=ledger.remaining_budget,
            remaining_slo=ledger.remaining_slo,
            checkpoints=ledger.checkpoints,
            paused_packets=ledger.paused_packets,
            reason_codes=ledger.reason_codes,
            ledger_hash=ledger.ledger_hash,
        )
        completion = run_completion_test(bad, bp, bus)
        # NEEDS_NEXT_NODE is not sealable.
        assert completion.completion_status == CompletionStatus.NEEDS_NEXT_NODE
        with pytest.raises(L3DoctrineContractError):
            seal_workflow_package(
                ledger=bad,
                blueprint=bp,
                context_bus=bus,
                completion=completion,
                request_id="r",
                run_id="rn",
                trace_root="tr",
                cost_summary=CostLatencyTokenSummary(),
            )
