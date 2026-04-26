"""03.6 L3 Managed Workflow Eligibility + DAG/HTN/AST Runner contracts.

Realizes:

- ``L3WorkflowInput``            — 03.6 PHASE 1 §1
- ``ExecutionShapeClassification`` — 03.6 PHASE 1 §2
- ``ManagedWorkflowBlueprint``   — 03.6 PHASE 1 §3
- ``WorkflowNode``                — 03.6 PHASE 1 §4
- ``WorkflowEdge``                — 03.6 PHASE 1 §5

DAG laws (03.6 §DAG LAWS):

- Forward-only graph for current run.
- No backward graph edges.
- Each node has a single owner layer.
- L3 does not retrieve, does not execute.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from . import L3DoctrineContractError

_MAX_STR = 512
_MAX_LIST = 256
_MAX_REASON = 32


def _need_str(value: object, name: str, *, allow_empty: bool = False) -> None:
    if not isinstance(value, str):
        raise L3DoctrineContractError(f"{name} must be str, got {type(value).__name__}")
    if len(value) > _MAX_STR:
        raise L3DoctrineContractError(f"{name} exceeds {_MAX_STR} chars")
    if not allow_empty and not value:
        raise L3DoctrineContractError(f"{name} must be non-empty")


def _need_str_tuple(values: object, name: str, *, max_len: int = _MAX_LIST) -> None:
    if not isinstance(values, tuple):
        raise L3DoctrineContractError(f"{name} must be tuple")
    if len(values) > max_len:
        raise L3DoctrineContractError(f"{name} exceeds {max_len}")
    for idx, item in enumerate(values):
        if not isinstance(item, str) or not item or len(item) > _MAX_STR:
            raise L3DoctrineContractError(f"{name}[{idx}] must be non-empty str <= {_MAX_STR}")


def _need_pos_int(value: object, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise L3DoctrineContractError(f"{name} must be int")
    if value < 0:
        raise L3DoctrineContractError(f"{name} must be >= 0")


def _need_bool(value: object, name: str) -> None:
    if not isinstance(value, bool):
        raise L3DoctrineContractError(f"{name} must be bool")


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class WorkflowExecutionForm(str, Enum):
    """L3 only operates on MANAGED_WORKFLOW. Restated for self-consistency."""

    MANAGED_WORKFLOW = "MANAGED_WORKFLOW"


class ExecutionShape(str, Enum):
    """03.6 §ExecutionShapeClassification.classification."""

    DIRECT_STEP_PACKAGE = "DIRECT_STEP_PACKAGE"
    MULTI_STEP_WORKFLOW = "MULTI_STEP_WORKFLOW"


class WorkflowNodeType(str, Enum):
    """03.6 §WorkflowNode.node_type — closed vocabulary."""

    C0_GROUNDING_STEP = "C0_GROUNDING_STEP"
    PROMPT_ASSEMBLY_STEP = "PROMPT_ASSEMBLY_STEP"
    L2_MODEL_STEP = "L2_MODEL_STEP"
    L2_TOOL_STEP = "L2_TOOL_STEP"
    L2_PTC_SANDBOX_STEP = "L2_PTC_SANDBOX_STEP"
    L2_SCRIPT_STEP = "L2_SCRIPT_STEP"
    L2_VALIDATION_STEP = "L2_VALIDATION_STEP"
    HITL_PAUSE_STEP = "HITL_PAUSE_STEP"
    MERGE_STEP = "MERGE_STEP"
    EVAL_LOOP_STEP = "EVAL_LOOP_STEP"


class EdgeDependencyType(str, Enum):
    """03.6 §WorkflowEdge.dependency_type."""

    DATA = "DATA"
    EVIDENCE = "EVIDENCE"
    POLICY = "POLICY"
    TOOL_CAPABILITY = "TOOL_CAPABILITY"
    GRAPH_CONTEXT = "GRAPH_CONTEXT"
    JOIN = "JOIN"
    HITL_RECLEARANCE = "HITL_RECLEARANCE"
    BUDGET = "BUDGET"
    QUALITY_THRESHOLD = "QUALITY_THRESHOLD"


# ---------------------------------------------------------------------------
# Substructures
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RouteSLOEnvelope:
    """SLO budget the workflow inherits from L0 RouteContract."""

    max_latency_ms: int
    max_cost: float
    max_tokens: int
    max_iterations: int

    def __post_init__(self) -> None:
        _need_pos_int(self.max_latency_ms, "RouteSLOEnvelope.max_latency_ms")
        _need_pos_int(self.max_tokens, "RouteSLOEnvelope.max_tokens")
        _need_pos_int(self.max_iterations, "RouteSLOEnvelope.max_iterations")
        if isinstance(self.max_cost, bool) or not isinstance(self.max_cost, (int, float)):
            raise L3DoctrineContractError("RouteSLOEnvelope.max_cost must be float")
        if self.max_cost != self.max_cost or self.max_cost < 0.0:
            raise L3DoctrineContractError("RouteSLOEnvelope.max_cost must be >= 0 and finite")


@dataclass(frozen=True)
class L3WorkflowInput:
    """03.6 PHASE 1 §1 L3WorkflowInput.

    Pre-condition: route_contract_id MUST refer to a RouteContract whose
    ``selected_route_id == R3R4_MANAGED_WORKFLOW`` and
    ``execution_form == MANAGED_WORKFLOW``. The caller validates this before
    instantiation; we record but do not re-fetch.
    """

    route_contract_id: str
    selected_route_id: str
    execution_form: WorkflowExecutionForm
    l1_plan_ref: str
    task_spec_ref: str
    query_spec_ref: str
    support_expectation: str
    action_expectation: str
    policy_hash: str
    blueprint_hash: str
    replay_key: str
    snapshot_id: str
    route_digest: str
    route_slo: RouteSLOEnvelope
    fallback_chain: tuple[str, ...]
    tenant_scope: str
    acl_scope: tuple[str, ...]
    capability_class: str
    sandbox_class: str
    workflow_blueprint_id: str = ""
    max_nodes: int = 32
    max_depth: int = 16
    max_iterations: int = 8
    max_parallelism: int = 4
    hitl_pause_points: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        for name in (
            "route_contract_id",
            "selected_route_id",
            "l1_plan_ref",
            "task_spec_ref",
            "query_spec_ref",
            "policy_hash",
            "blueprint_hash",
            "replay_key",
            "snapshot_id",
            "route_digest",
            "tenant_scope",
            "capability_class",
            "sandbox_class",
        ):
            _need_str(getattr(self, name), f"L3WorkflowInput.{name}")
        for name in ("support_expectation", "action_expectation", "workflow_blueprint_id"):
            _need_str(getattr(self, name), f"L3WorkflowInput.{name}", allow_empty=True)
        # 03.6 §ENTRY LAW: L3 must refuse anything other than MANAGED_WORKFLOW.
        if self.selected_route_id != "R3R4_MANAGED_WORKFLOW":
            raise L3DoctrineContractError(
                f"L3 only operates on R3R4_MANAGED_WORKFLOW; got {self.selected_route_id}",
            )
        if not isinstance(self.execution_form, WorkflowExecutionForm):
            raise L3DoctrineContractError(
                "L3WorkflowInput.execution_form must be WorkflowExecutionForm",
            )
        if not isinstance(self.route_slo, RouteSLOEnvelope):
            raise L3DoctrineContractError("L3WorkflowInput.route_slo must be RouteSLOEnvelope")
        _need_str_tuple(self.fallback_chain, "L3WorkflowInput.fallback_chain", max_len=_MAX_REASON)
        _need_str_tuple(self.acl_scope, "L3WorkflowInput.acl_scope")
        _need_str_tuple(
            self.hitl_pause_points,
            "L3WorkflowInput.hitl_pause_points",
            max_len=_MAX_REASON,
        )
        for name in ("max_nodes", "max_depth", "max_iterations", "max_parallelism"):
            _need_pos_int(getattr(self, name), f"L3WorkflowInput.{name}")
        # 03.6 §ENTRY LAW + §ACCEPTANCE — Missing max_iterations fails closed.
        if self.max_iterations == 0:
            raise L3DoctrineContractError("L3WorkflowInput.max_iterations must be > 0")
        if self.max_nodes == 0:
            raise L3DoctrineContractError("L3WorkflowInput.max_nodes must be > 0")


@dataclass(frozen=True)
class ExecutionShapeClassification:
    """03.6 PHASE 1 §2 ExecutionShapeClassification."""

    classification_id: str
    classification: ExecutionShape
    why_not_single_step: tuple[str, ...]
    why_not_workflow: tuple[str, ...]
    changing_step_contracts: tuple[str, ...]
    dependency_chain_detected: bool
    branching_detected: bool
    join_detected: bool
    staged_evidence_required: bool
    parallel_shards_detected: bool
    hitl_pause_resume_required: bool
    checkpoint_resume_required: bool
    evaluator_optimizer_loop_required: bool
    ptc_step_candidate_detected: bool
    classification_hash: str

    def __post_init__(self) -> None:
        _need_str(self.classification_id, "ExecutionShapeClassification.classification_id")
        _need_str(self.classification_hash, "ExecutionShapeClassification.classification_hash")
        if not isinstance(self.classification, ExecutionShape):
            raise L3DoctrineContractError(
                "ExecutionShapeClassification.classification must be ExecutionShape",
            )
        for name in (
            "why_not_single_step",
            "why_not_workflow",
            "changing_step_contracts",
        ):
            _need_str_tuple(getattr(self, name), f"ExecutionShapeClassification.{name}", max_len=_MAX_REASON)
        for name in (
            "dependency_chain_detected",
            "branching_detected",
            "join_detected",
            "staged_evidence_required",
            "parallel_shards_detected",
            "hitl_pause_resume_required",
            "checkpoint_resume_required",
            "evaluator_optimizer_loop_required",
            "ptc_step_candidate_detected",
        ):
            _need_bool(getattr(self, name), f"ExecutionShapeClassification.{name}")
        # Coherence: MULTI_STEP_WORKFLOW requires at least one structural reason.
        if self.classification == ExecutionShape.MULTI_STEP_WORKFLOW:
            structural = (
                self.dependency_chain_detected
                or self.branching_detected
                or self.join_detected
                or self.staged_evidence_required
                or self.parallel_shards_detected
                or self.hitl_pause_resume_required
                or self.checkpoint_resume_required
                or self.evaluator_optimizer_loop_required
            )
            if not structural:
                raise L3DoctrineContractError(
                    "MULTI_STEP_WORKFLOW classification requires at least one structural reason",
                )


@dataclass(frozen=True)
class WorkflowNode:
    """03.6 PHASE 1 §4 WorkflowNode."""

    node_id: str
    node_type: WorkflowNodeType
    current_ask: str
    required_inputs: tuple[str, ...]
    expected_outputs: tuple[str, ...]
    support_target: str
    capability_requirement: str
    sandbox_requirement: str
    max_attempts: int
    timeout_ms: int
    cost_budget: float
    retry_policy: str
    fallback_policy: str
    ptc_allowed_if_l2_step: bool = False
    no_direct_execution_assertion: bool = True

    def __post_init__(self) -> None:
        for name in (
            "node_id",
            "current_ask",
            "support_target",
            "capability_requirement",
            "sandbox_requirement",
            "retry_policy",
            "fallback_policy",
        ):
            _need_str(getattr(self, name), f"WorkflowNode.{name}", allow_empty=(name == "current_ask"))
        # node_id must be non-empty
        if not self.node_id:
            raise L3DoctrineContractError("WorkflowNode.node_id must be non-empty")
        if not isinstance(self.node_type, WorkflowNodeType):
            raise L3DoctrineContractError("WorkflowNode.node_type must be WorkflowNodeType")
        _need_str_tuple(self.required_inputs, "WorkflowNode.required_inputs", max_len=_MAX_LIST)
        _need_str_tuple(self.expected_outputs, "WorkflowNode.expected_outputs", max_len=_MAX_LIST)
        for name in ("max_attempts", "timeout_ms"):
            _need_pos_int(getattr(self, name), f"WorkflowNode.{name}")
        if self.max_attempts == 0:
            raise L3DoctrineContractError("WorkflowNode.max_attempts must be > 0")
        if isinstance(self.cost_budget, bool) or not isinstance(self.cost_budget, (int, float)):
            raise L3DoctrineContractError("WorkflowNode.cost_budget must be float")
        if self.cost_budget != self.cost_budget or self.cost_budget < 0.0:
            raise L3DoctrineContractError("WorkflowNode.cost_budget must be >= 0 and finite")
        for name in ("ptc_allowed_if_l2_step", "no_direct_execution_assertion"):
            _need_bool(getattr(self, name), f"WorkflowNode.{name}")
        # 03.6 §DAG LAWS — PTC node is L2_PTC_SANDBOX_STEP only.
        if self.ptc_allowed_if_l2_step and self.node_type not in {
            WorkflowNodeType.L2_PTC_SANDBOX_STEP,
            WorkflowNodeType.L2_TOOL_STEP,
            WorkflowNodeType.L2_SCRIPT_STEP,
        }:
            raise L3DoctrineContractError(
                f"ptc_allowed_if_l2_step=True requires L2_*_STEP node_type, got {self.node_type.value}",
            )
        if not self.no_direct_execution_assertion:
            raise L3DoctrineContractError(
                "WorkflowNode.no_direct_execution_assertion must be True (L3 does not execute)",
            )


@dataclass(frozen=True)
class WorkflowEdge:
    """03.6 PHASE 1 §5 WorkflowEdge."""

    edge_id: str
    from_node: str
    to_node: str
    dependency_type: EdgeDependencyType
    condition: str = ""
    edge_order: int = 0
    branch_label: str = ""
    join_group: str = ""
    replay_order_key: str = ""

    def __post_init__(self) -> None:
        _need_str(self.edge_id, "WorkflowEdge.edge_id")
        _need_str(self.from_node, "WorkflowEdge.from_node")
        _need_str(self.to_node, "WorkflowEdge.to_node")
        if self.from_node == self.to_node:
            raise L3DoctrineContractError(
                f"WorkflowEdge from_node==to_node ({self.from_node}); self-loop forbidden",
            )
        if not isinstance(self.dependency_type, EdgeDependencyType):
            raise L3DoctrineContractError("WorkflowEdge.dependency_type must be EdgeDependencyType")
        for name in ("condition", "branch_label", "join_group", "replay_order_key"):
            _need_str(getattr(self, name), f"WorkflowEdge.{name}", allow_empty=True)
        _need_pos_int(self.edge_order, "WorkflowEdge.edge_order")


@dataclass(frozen=True)
class ManagedWorkflowBlueprint:
    """03.6 PHASE 1 §3 ManagedWorkflowBlueprint."""

    workflow_id: str
    route_contract_id: str
    workflow_blueprint_id: str
    nodes: tuple[WorkflowNode, ...]
    edges: tuple[WorkflowEdge, ...]
    branch_policy: str
    join_policy: str
    retry_policy: str
    fallback_policy: str
    parallelism_policy: str
    checkpoint_policy: str
    hitl_pause_policy: str
    quality_loop_policy: str
    evidence_merge_policy: str
    contradiction_policy: str
    completion_policy: str
    replay_metadata: tuple[str, ...]
    graph_hash: str
    dependency_types: tuple[EdgeDependencyType, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        for name in (
            "workflow_id",
            "route_contract_id",
            "workflow_blueprint_id",
            "branch_policy",
            "join_policy",
            "retry_policy",
            "fallback_policy",
            "parallelism_policy",
            "checkpoint_policy",
            "hitl_pause_policy",
            "quality_loop_policy",
            "evidence_merge_policy",
            "contradiction_policy",
            "completion_policy",
            "graph_hash",
        ):
            _need_str(getattr(self, name), f"ManagedWorkflowBlueprint.{name}")
        if not isinstance(self.nodes, tuple) or len(self.nodes) == 0:
            raise L3DoctrineContractError(
                "ManagedWorkflowBlueprint.nodes must be a non-empty tuple of WorkflowNode",
            )
        if len(self.nodes) > _MAX_LIST:
            raise L3DoctrineContractError(
                f"ManagedWorkflowBlueprint.nodes exceeds {_MAX_LIST}",
            )
        node_ids: set[str] = set()
        for n in self.nodes:
            if not isinstance(n, WorkflowNode):
                raise L3DoctrineContractError(
                    f"ManagedWorkflowBlueprint.nodes must all be WorkflowNode; got {type(n).__name__}",
                )
            if n.node_id in node_ids:
                raise L3DoctrineContractError(
                    f"ManagedWorkflowBlueprint duplicate node_id {n.node_id!r}",
                )
            node_ids.add(n.node_id)
        if not isinstance(self.edges, tuple):
            raise L3DoctrineContractError("ManagedWorkflowBlueprint.edges must be tuple")
        if len(self.edges) > _MAX_LIST:
            raise L3DoctrineContractError(f"ManagedWorkflowBlueprint.edges exceeds {_MAX_LIST}")
        for e in self.edges:
            if not isinstance(e, WorkflowEdge):
                raise L3DoctrineContractError(
                    f"ManagedWorkflowBlueprint.edges must all be WorkflowEdge; got {type(e).__name__}",
                )
            if e.from_node not in node_ids or e.to_node not in node_ids:
                raise L3DoctrineContractError(
                    f"WorkflowEdge {e.edge_id} references unknown node ({e.from_node!r} -> {e.to_node!r})",
                )
        # 03.6 §DAG LAWS — forward-only: no cycles.
        if _has_cycle(self.nodes, self.edges):
            raise L3DoctrineContractError(
                "ManagedWorkflowBlueprint contains a cycle; DAG must be forward-only",
            )
        _need_str_tuple(
            self.replay_metadata,
            "ManagedWorkflowBlueprint.replay_metadata",
            max_len=_MAX_REASON,
        )
        if not isinstance(self.dependency_types, tuple):
            raise L3DoctrineContractError(
                "ManagedWorkflowBlueprint.dependency_types must be tuple",
            )
        for dt in self.dependency_types:
            if not isinstance(dt, EdgeDependencyType):
                raise L3DoctrineContractError(
                    "ManagedWorkflowBlueprint.dependency_types entries must be EdgeDependencyType",
                )


def _has_cycle(
    nodes: tuple[WorkflowNode, ...],
    edges: tuple[WorkflowEdge, ...],
) -> bool:
    """Plain DFS-based cycle check on the node set."""
    adj: dict[str, list[str]] = {n.node_id: [] for n in nodes}
    for e in edges:
        adj[e.from_node].append(e.to_node)
    visiting: set[str] = set()
    visited: set[str] = set()

    def _dfs(u: str) -> bool:
        visiting.add(u)
        for v in adj.get(u, ()):
            if v in visiting:
                return True
            if v not in visited and _dfs(v):
                return True
        visiting.discard(u)
        visited.add(u)
        return False

    return any(_dfs(n.node_id) for n in nodes if n.node_id not in visited)


__all__ = [
    "EdgeDependencyType",
    "ExecutionShape",
    "ExecutionShapeClassification",
    "L3WorkflowInput",
    "ManagedWorkflowBlueprint",
    "RouteSLOEnvelope",
    "WorkflowEdge",
    "WorkflowExecutionForm",
    "WorkflowNode",
    "WorkflowNodeType",
]
