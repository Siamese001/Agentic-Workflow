"""Unit tests for agentic_core.L3_orchestration.doctrine.contracts_l3_6.

Wave 6.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — untested P2 L3 doctrine
contracts. 03.6 Workflow Eligibility + DAG: frozen dataclasses, closed-vocabulary
enums, __post_init__ invariant raises (all via L3DoctrineContractError), and the
forward-only DAG cycle check inside ManagedWorkflowBlueprint.

Pure/deterministic surface only — no I/O, no mocks.
"""

from __future__ import annotations

import dataclasses

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


def _node(node_id: str = "n1", node_type: WorkflowNodeType = WorkflowNodeType.L2_MODEL_STEP) -> WorkflowNode:
    return WorkflowNode(
        node_id=node_id,
        node_type=node_type,
        current_ask="",
        required_inputs=(),
        expected_outputs=(),
        support_target="support",
        capability_requirement="cap",
        sandbox_requirement="sandbox",
        max_attempts=1,
        timeout_ms=1000,
        cost_budget=1.0,
        retry_policy="none",
        fallback_policy="none",
    )


def _edge(edge_id: str, from_node: str, to_node: str) -> WorkflowEdge:
    return WorkflowEdge(
        edge_id=edge_id,
        from_node=from_node,
        to_node=to_node,
        dependency_type=EdgeDependencyType.DATA,
    )


def _slo() -> RouteSLOEnvelope:
    return RouteSLOEnvelope(max_latency_ms=1000, max_cost=1.0, max_tokens=100, max_iterations=4)


class TestEnums:
    def test_execution_form_members(self) -> None:
        assert {m.value for m in WorkflowExecutionForm} == {"MANAGED_WORKFLOW"}

    def test_execution_shape_members(self) -> None:
        assert {m.value for m in ExecutionShape} == {
            "DIRECT_STEP_PACKAGE",
            "MULTI_STEP_WORKFLOW",
        }

    def test_node_type_members(self) -> None:
        assert {m.value for m in WorkflowNodeType} == {
            "C0_GROUNDING_STEP",
            "PROMPT_ASSEMBLY_STEP",
            "L2_MODEL_STEP",
            "L2_TOOL_STEP",
            "L2_PTC_SANDBOX_STEP",
            "L2_SCRIPT_STEP",
            "L2_VALIDATION_STEP",
            "HITL_PAUSE_STEP",
            "MERGE_STEP",
            "EVAL_LOOP_STEP",
        }

    def test_edge_dependency_members(self) -> None:
        assert {m.value for m in EdgeDependencyType} == {
            "DATA",
            "EVIDENCE",
            "POLICY",
            "TOOL_CAPABILITY",
            "GRAPH_CONTEXT",
            "JOIN",
            "HITL_RECLEARANCE",
            "BUDGET",
            "QUALITY_THRESHOLD",
        }

    def test_enums_are_str_enums(self) -> None:
        assert ExecutionShape.MULTI_STEP_WORKFLOW == "MULTI_STEP_WORKFLOW"
        assert WorkflowNodeType.MERGE_STEP == "MERGE_STEP"


class TestRouteSLOEnvelope:
    def test_construct_ok(self) -> None:
        slo = _slo()
        assert slo.max_latency_ms == 1000

    def test_negative_latency_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="max_latency_ms"):
            RouteSLOEnvelope(max_latency_ms=-1, max_cost=1.0, max_tokens=1, max_iterations=1)

    def test_negative_cost_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="max_cost must be >= 0"):
            RouteSLOEnvelope(max_latency_ms=1, max_cost=-1.0, max_tokens=1, max_iterations=1)

    def test_nan_cost_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="max_cost must be >= 0"):
            RouteSLOEnvelope(max_latency_ms=1, max_cost=float("nan"), max_tokens=1, max_iterations=1)

    def test_bool_cost_rejected(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="max_cost must be float"):
            RouteSLOEnvelope(max_latency_ms=1, max_cost=True, max_tokens=1, max_iterations=1)  # type: ignore[arg-type]

    def test_frozen(self) -> None:
        with pytest.raises(dataclasses.FrozenInstanceError):
            _slo().max_tokens = 5  # type: ignore[misc]


class TestWorkflowNode:
    def test_defaults(self) -> None:
        n = _node()
        assert n.ptc_allowed_if_l2_step is False
        assert n.no_direct_execution_assertion is True

    def test_empty_node_id_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            _node(node_id="")

    @pytest.mark.parametrize(
        "node_type",
        [
            WorkflowNodeType.L2_PTC_SANDBOX_STEP,
            WorkflowNodeType.L2_TOOL_STEP,
            WorkflowNodeType.L2_SCRIPT_STEP,
        ],
    )
    def test_ptc_allowed_on_l2_node_types(self, node_type: WorkflowNodeType) -> None:
        n = dataclasses.replace(_node(node_type=node_type), ptc_allowed_if_l2_step=True)
        assert n.ptc_allowed_if_l2_step is True

    def test_ptc_allowed_on_non_l2_node_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="ptc_allowed_if_l2_step"):
            WorkflowNode(
                node_id="n",
                node_type=WorkflowNodeType.MERGE_STEP,
                current_ask="",
                required_inputs=(),
                expected_outputs=(),
                support_target="s",
                capability_requirement="c",
                sandbox_requirement="sb",
                max_attempts=1,
                timeout_ms=1,
                cost_budget=0.0,
                retry_policy="r",
                fallback_policy="f",
                ptc_allowed_if_l2_step=True,
            )

    def test_zero_max_attempts_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="max_attempts must be > 0"):
            dataclasses.replace(_node(), max_attempts=0)

    def test_no_direct_execution_false_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="no_direct_execution_assertion"):
            dataclasses.replace(_node(), no_direct_execution_assertion=False)

    def test_negative_cost_budget_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="cost_budget"):
            dataclasses.replace(_node(), cost_budget=-1.0)


class TestWorkflowEdge:
    def test_construct_ok(self) -> None:
        e = _edge("e1", "a", "b")
        assert e.edge_order == 0
        assert e.condition == ""

    def test_self_loop_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="self-loop forbidden"):
            _edge("e1", "a", "a")

    def test_negative_edge_order_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="edge_order"):
            WorkflowEdge(
                edge_id="e",
                from_node="a",
                to_node="b",
                dependency_type=EdgeDependencyType.DATA,
                edge_order=-1,
            )

    def test_bad_dependency_type_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="dependency_type"):
            WorkflowEdge(
                edge_id="e",
                from_node="a",
                to_node="b",
                dependency_type="DATA",  # type: ignore[arg-type]
            )


class TestExecutionShapeClassification:
    def _kwargs(self, **overrides: object) -> dict:
        base = dict(
            classification_id="c1",
            classification=ExecutionShape.DIRECT_STEP_PACKAGE,
            why_not_single_step=(),
            why_not_workflow=(),
            changing_step_contracts=(),
            dependency_chain_detected=False,
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
        return base

    def test_direct_step_package_ok_without_structural_reason(self) -> None:
        c = ExecutionShapeClassification(**self._kwargs())
        assert c.classification == ExecutionShape.DIRECT_STEP_PACKAGE

    def test_multi_step_without_structural_reason_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="structural reason"):
            ExecutionShapeClassification(
                **self._kwargs(classification=ExecutionShape.MULTI_STEP_WORKFLOW)
            )

    def test_multi_step_with_structural_reason_ok(self) -> None:
        c = ExecutionShapeClassification(
            **self._kwargs(
                classification=ExecutionShape.MULTI_STEP_WORKFLOW,
                branching_detected=True,
            )
        )
        assert c.branching_detected is True

    def test_non_bool_flag_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError):
            ExecutionShapeClassification(**self._kwargs(join_detected="yes"))  # type: ignore[arg-type]


class TestL3WorkflowInput:
    def _kwargs(self, **overrides: object) -> dict:
        base = dict(
            route_contract_id="rc1",
            selected_route_id="R3R4_MANAGED_WORKFLOW",
            execution_form=WorkflowExecutionForm.MANAGED_WORKFLOW,
            l1_plan_ref="plan",
            task_spec_ref="task",
            query_spec_ref="query",
            support_expectation="",
            action_expectation="",
            policy_hash="ph",
            blueprint_hash="bh",
            replay_key="rk",
            snapshot_id="sid",
            route_digest="rd",
            route_slo=_slo(),
            fallback_chain=(),
            tenant_scope="tenant",
            acl_scope=(),
            capability_class="cap",
            sandbox_class="sb",
        )
        base.update(overrides)
        return base

    def test_construct_ok_defaults(self) -> None:
        wi = L3WorkflowInput(**self._kwargs())
        assert wi.max_nodes == 32
        assert wi.max_depth == 16

    def test_wrong_route_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="R3R4_MANAGED_WORKFLOW"):
            L3WorkflowInput(**self._kwargs(selected_route_id="R1_DIRECT"))

    def test_zero_max_iterations_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="max_iterations must be > 0"):
            L3WorkflowInput(**self._kwargs(max_iterations=0))

    def test_zero_max_nodes_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="max_nodes must be > 0"):
            L3WorkflowInput(**self._kwargs(max_nodes=0))

    def test_bad_execution_form_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="execution_form"):
            L3WorkflowInput(**self._kwargs(execution_form="MANAGED_WORKFLOW"))  # type: ignore[arg-type]

    def test_bad_route_slo_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="route_slo"):
            L3WorkflowInput(**self._kwargs(route_slo=object()))


class TestManagedWorkflowBlueprint:
    def _kwargs(self, **overrides: object) -> dict:
        base = dict(
            workflow_id="wf",
            route_contract_id="rc",
            workflow_blueprint_id="bp",
            nodes=(_node("a"), _node("b")),
            edges=(_edge("e1", "a", "b"),),
            branch_policy="bp",
            join_policy="jp",
            retry_policy="rp",
            fallback_policy="fp",
            parallelism_policy="pp",
            checkpoint_policy="cp",
            hitl_pause_policy="hp",
            quality_loop_policy="qp",
            evidence_merge_policy="ep",
            contradiction_policy="cdp",
            completion_policy="comp",
            replay_metadata=(),
            graph_hash="gh",
        )
        base.update(overrides)
        return base

    def test_construct_ok(self) -> None:
        bp = ManagedWorkflowBlueprint(**self._kwargs())
        assert len(bp.nodes) == 2
        assert bp.dependency_types == ()

    def test_empty_nodes_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="non-empty tuple"):
            ManagedWorkflowBlueprint(**self._kwargs(nodes=(), edges=()))

    def test_duplicate_node_id_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="duplicate node_id"):
            ManagedWorkflowBlueprint(**self._kwargs(nodes=(_node("a"), _node("a")), edges=()))

    def test_edge_references_unknown_node_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="unknown node"):
            ManagedWorkflowBlueprint(
                **self._kwargs(nodes=(_node("a"),), edges=(_edge("e", "a", "z"),))
            )

    def test_cycle_raises(self) -> None:
        nodes = (_node("a"), _node("b"))
        edges = (_edge("e1", "a", "b"), _edge("e2", "b", "a"))
        with pytest.raises(L3DoctrineContractError, match="cycle"):
            ManagedWorkflowBlueprint(**self._kwargs(nodes=nodes, edges=edges))

    def test_acyclic_chain_ok(self) -> None:
        nodes = (_node("a"), _node("b"), _node("c"))
        edges = (_edge("e1", "a", "b"), _edge("e2", "b", "c"))
        bp = ManagedWorkflowBlueprint(**self._kwargs(nodes=nodes, edges=edges))
        assert len(bp.edges) == 2

    def test_bad_dependency_types_entry_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="dependency_types"):
            ManagedWorkflowBlueprint(**self._kwargs(dependency_types=("DATA",)))  # type: ignore[arg-type]
