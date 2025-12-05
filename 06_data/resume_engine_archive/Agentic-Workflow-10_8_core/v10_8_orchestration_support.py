"""
V10.8 Consolidated Module: Orchestration Support
Merged from 8 source files
"""

# Consolidated imports
from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass
from dataclasses import dataclass, field
from errors_controlflow import DAGValidationError
from errors_controlflow import NodeExecutionError
from l3_orchestration import DAG
from meta_profile import META_PROFILE
from multi_agent import AgentRole
from node_result import NodeResult
from node_result import NodeResult, NodeStatus
from typing import Any, Callable, Dict, List, Optional
from typing import Any, Dict
from typing import Any, Dict, List, Set
from typing import Dict, Any
from typing import List, Dict, Any


# ============================================================
# From v10_8_dag_executor.py
# ============================================================

class DAGExecutor:
    """Deterministic executor for DAG nodes with retry logic."""

    def run(self, dag: DAG, initial_context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        dag.validate()
        context: Dict[str, Any] = deepcopy(initial_context) if initial_context else {}

        parents = self._build_parents_map(dag)
        ready: List[str] = sorted([name for name, deps in parents.items() if not deps])
        executed: Set[str] = set()

        while ready:
            node_name = ready.pop(0)
            if node_name in executed:
                continue

            node = dag.nodes[node_name]
            result, attempted_nodes = self._execute_with_retries(node_name, node, context)

            if result.status is NodeStatus.SUCCESS:
                context.update(result.payload)
                if node.parallel:
                    context = self._execute_parallel_nodes(dag, node.parallel, context, executed)
                outgoing = self._determine_edges(dag, node, context)
            else:
                outgoing = [node.fallback_edge] if node.fallback_edge else []

            executed.update(attempted_nodes)
            executed.add(node_name)
            self._enqueue_targets(outgoing, dag, parents, executed, ready)

        return context

    def _execute_with_retries(
        self, node_name: str, node: Any, context: Dict[str, Any]
    ) -> tuple[NodeResult, Set[str]]:
        attempted: Set[str] = set()
        attempts = node.retries + 1
        last_result: NodeResult | None = None
        for _ in range(attempts):
            last_result = node.run(deepcopy(context))
            attempted.add(node_name)
            if last_result.status is NodeStatus.SUCCESS:
                return last_result, attempted
        assert last_result is not None
        return NodeResult(NodeStatus.FAILURE, last_result.payload), attempted

    def _determine_edges(self, dag: DAG, node: Any, context: Dict[str, Any]) -> List[str]:
        if node.condition:
            try:
                condition_result = bool(node.condition(context))
            except Exception:
                condition_result = False
            if condition_result:
                return node.conditional_edges.get("condition_true", [])
        return dag.edges.get(node.name, [])

    def _build_parents_map(self, dag: DAG) -> Dict[str, Set[str]]:
        parents: Dict[str, Set[str]] = {name: set() for name in dag.nodes}
        for source, targets in dag.edges.items():
            for target in targets:
                parents[target].add(source)
        for node in dag.nodes.values():
            for conditional_targets in node.conditional_edges.values():
                for target in conditional_targets:
                    parents[target].add(node.name)
        return parents

    def _enqueue_targets(
        self,
        targets: List[str],
        dag: DAG,
        parents: Dict[str, Set[str]],
        executed: Set[str],
        ready: List[str],
    ) -> None:
        for target in targets:
            if target not in dag.nodes:
                raise NodeExecutionError(
                    f"Edge target '{target}' is not a defined node in the DAG."
                )
            if parents.get(target, set()).issubset(executed) and target not in ready:
                ready.append(target)
        ready.sort()

    def _execute_parallel_nodes(
        self, dag: DAG, parallel_nodes: List[str], context: Dict[str, Any], executed: Set[str]
    ) -> Dict[str, Any]:
        merged = deepcopy(context)
        for child_name in sorted(parallel_nodes):
            if child_name not in dag.nodes:
                raise NodeExecutionError(
                    f"Parallel target '{child_name}' is not a defined node in the DAG."
                )
            child_node = dag.nodes[child_name]
            child_result, _ = self._execute_with_retries(child_name, child_node, merged)
            merged.update(child_result.payload)
            executed.add(child_name)
        return merged

# ============================================================
# From v10_8_dag_spec.py
# ============================================================

@dataclass
class DAGNode:
    """Structural node definition for DAG orchestration."""

    name: str
    run: Callable[[Dict[str, Any]], NodeResult]
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None
    conditional_edges: Dict[str, List[str]] = field(default_factory=dict)
    retries: int = 0
    fallback_edge: Optional[str] = None
    parallel: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.name:
            raise DAGValidationError("DAG nodes require a non-empty name.")


@dataclass
class DAG:
    """A directed acyclic graph of orchestration steps."""

    nodes: Dict[str, DAGNode]
    edges: Dict[str, List[str]]

    def validate(self) -> None:
        """Validate the DAG is well-formed and acyclic."""

        if not self.nodes:
            raise DAGValidationError("DAG must define at least one node.")

        for node_name, node in self.nodes.items():
            if node_name != node.name:
                raise DAGValidationError(
                    f"Node key '{node_name}' does not match node name '{node.name}'."
                )

        for source, targets in self.edges.items():
            if source not in self.nodes:
                raise DAGValidationError(f"Edge source '{source}' is not a defined node.")
            for target in targets:
                if target not in self.nodes:
                    raise DAGValidationError(
                        f"Edge target '{target}' from '{source}' is not a defined node."
                    )

    def topological_sort(self) -> List[str]:
        """Return a deterministic topological ordering of the DAG nodes."""

        self.validate()
        in_degree: Dict[str, int] = {name: 0 for name in self.nodes}
        for targets in self.edges.values():
            for target in targets:
                in_degree[target] += 1

        ready = sorted([name for name, degree in in_degree.items() if degree == 0])
        order: List[str] = []

        while ready:
            current = ready.pop(0)
            order.append(current)
            for neighbor in sorted(self.edges.get(current, [])):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    ready.append(neighbor)

        if len(order) != len(self.nodes):
            raise DAGValidationError("DAG contains cycles; topological sort failed.")

        return order

# ============================================================
# From v10_8_routing.py
# ============================================================

@dataclass
class RoutingCriteria:
    task_type: str
    complexity: str = "low"  # low | medium | high
    latency_target_ms: int = 2000
    cost_ceiling_usd: float = 0.05
    risk_level: str = "normal"  # normal | strict | high_safety
    model_available: bool = True


@dataclass
class RoutingDecision:
    model: str
    endpoint: str
    rationale: str


def decide_route(criteria: RoutingCriteria) -> RoutingDecision:
    """
    Deterministic routing strategy based on criteria.
    No external calls, no randomness.
    """
    # Simple deterministic mapping:
    if criteria.complexity == "high" or criteria.risk_level == "strict":
        decision = RoutingDecision(
            model="gpt-4o",
            endpoint="default",
            rationale="High complexity or strict risk requires GPT-4o.",
        )
    elif criteria.latency_target_ms < 1000:
        decision = RoutingDecision(
            model="gpt-4o-mini",
            endpoint="fast",
            rationale="Low latency target; use lightweight model.",
        )
    else:
        decision = RoutingDecision(
            model="gpt-4o-mini",
            endpoint="default",
            rationale="Default routing for normal tasks.",
        )

    if not criteria.model_available:
        decision = RoutingDecision(
            model="gpt-4o-mini",
            endpoint="fast",
            rationale="Primary route unavailable; using fallback fast endpoint.",
        )

    if META_PROFILE.routing_bias.get("prefer_fast") and decision.endpoint in (
        "fast",
        "default",
    ):
        decision = RoutingDecision(
            model=decision.model,
            endpoint="fast",
            rationale=decision.rationale,
        )

    return decision
from typing import Dict, Any

from model_invocation import invoke_model


class ModelClient:
    """Abstract client for model execution. Deterministic stub only."""

    def __init__(self, route_metadata: Dict[str, Any] | None = None) -> None:
        self.route_metadata = route_metadata or {}

    def complete(self, prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke the deterministic stub with a fully rendered prompt."""

        merged_metadata = {**self.route_metadata, **(config or {})}
        return invoke_model(prompt, merged_metadata)


def build_client_for_route(route: Dict[str, Any]) -> ModelClient:
    # Return a new client bound to route metadata; side-effect free
    return ModelClient(route)


def configure_for_routing(route: Dict[str, Any]) -> Dict[str, Any]:
    selected_model = route.get("selected_model") or route.get("model")
    model_name = selected_model or "stub-model-for-" + route.get("complexity", "default")
    endpoint = route.get("endpoint") or "/v1/" + route.get("complexity", "default")
    return {
        "model": model_name,
        "model_name": model_name,
        "endpoint": endpoint,
        "route": route,
    }


def run_model_for_plan(plan: Dict[str, Any], state: Dict[str, Any]):
    from prompt_utils import build_prompt_from_plan_and_state

    rendered = build_prompt_from_plan_and_state(plan, state)
    routing_plan = get_routing_plan(plan)

    safety_metadata = plan.get("safety_metadata", {}) if isinstance(plan, dict) else {}
    latency_seconds = routing_plan.get("latency_target", 0)
    try:
        latency_ms = int(latency_seconds * 1000)
    except Exception:
        latency_ms = 0

    criteria = RoutingCriteria(
        task_type=str(plan.get("mode", "unknown")),
        complexity=str(routing_plan.get("complexity", "low")),
        latency_target_ms=latency_ms,
        cost_ceiling_usd=float(routing_plan.get("cost_ceiling", 0.0)),
        risk_level=str(
            routing_plan.get(
                "risk_level", "strict" if safety_metadata.get("sensitivity") == "high" else "normal"
            )
        ),
    )
    decision = decide_route(criteria)
    routing_dict = {
        "selected_model": decision.model,
        "endpoint": decision.endpoint,
        "rationale": decision.rationale,
    }

    routing_plan.update(routing_dict)
    plan["routing"] = routing_plan

    client = build_client_for_route(routing_dict)
    config = configure_for_routing(routing_dict)
    result = client.complete(rendered["prompt"], config)

    return {
        "prompt": rendered["prompt"],
        "model_output": result,
        "routing": routing_dict,
    }
from typing import Any, Dict


def get_routing_plan(plan: Dict[str, Any]) -> Dict[str, Any]:
    return plan.get("routing", {}).copy()


def get_routing_model_name(plan: Dict[str, Any]) -> str:
    routing = plan.get("routing", {})
    return routing.get("selected_model") or routing.get("complexity", "unknown")


def get_routing_metadata(plan: Dict[str, Any]) -> Dict[str, Any]:
    return plan.get("routing", {}).copy()

# ============================================================
# From v10_8_routing_policy.py
# ============================================================

@dataclass
class RoutingCriteria:
    task_type: str
    complexity: str = "low"  # low | medium | high
    latency_target_ms: int = 2000
    cost_ceiling_usd: float = 0.05
    risk_level: str = "normal"  # normal | strict | high_safety
    model_available: bool = True


@dataclass
class RoutingDecision:
    model: str
    endpoint: str
    rationale: str


def decide_route(criteria: RoutingCriteria) -> RoutingDecision:
    """
    Deterministic routing strategy based on criteria.
    No external calls, no randomness.
    """
    # Simple deterministic mapping:
    if criteria.complexity == "high" or criteria.risk_level == "strict":
        decision = RoutingDecision(
            model="gpt-4o",
            endpoint="default",
            rationale="High complexity or strict risk requires GPT-4o.",
        )
    elif criteria.latency_target_ms < 1000:
        decision = RoutingDecision(
            model="gpt-4o-mini",
            endpoint="fast",
            rationale="Low latency target; use lightweight model.",
        )
    else:
        decision = RoutingDecision(
            model="gpt-4o-mini",
            endpoint="default",
            rationale="Default routing for normal tasks.",
        )

    if not criteria.model_available:
        decision = RoutingDecision(
            model="gpt-4o-mini",
            endpoint="fast",
            rationale="Primary route unavailable; using fallback fast endpoint.",
        )

    if META_PROFILE.routing_bias.get("prefer_fast") and decision.endpoint in (
        "fast",
        "default",
    ):
        decision = RoutingDecision(
            model=decision.model,
            endpoint="fast",
            rationale=decision.rationale,
        )

    return decision

# ============================================================
# From v10_8_routing_views.py
# ============================================================

def get_routing_plan(plan: Dict[str, Any]) -> Dict[str, Any]:
    return plan.get("routing", {}).copy()


def get_routing_model_name(plan: Dict[str, Any]) -> str:
    routing = plan.get("routing", {})
    return routing.get("selected_model") or routing.get("complexity", "unknown")


def get_routing_metadata(plan: Dict[str, Any]) -> Dict[str, Any]:
    return plan.get("routing", {}).copy()

# ============================================================
# From v10_8_arbitration_engine.py
# ============================================================

class ArbitrationEngine:
    """
    Deterministic stub arbitration engine.

    evaluate(state, qa_report, safety_patch) -> Dict[str,str]
    returns one of: accept, retry, replan, escalate
    """

    def evaluate(self, state: Dict[str, Any], qa_report: Dict[str, Any], safety_patch: Dict[str, Any]) -> Dict[str, str]:
        # 1) If safety is blocked → escalate
        sg = safety_patch.get("safety_gateway", {})
        if sg.get("status") == "blocked":
            return {
                "action": "escalate",
                "reason": "safety_blocked",
                "surface_hint": "strategy_replan",
            }

        # 2) If QA findings are pending → retry
        findings = qa_report.get("findings", [])
        for f in findings:
            if f.get("status") == "pending":
                return {
                    "action": "retry",
                    "reason": "qa_pending",
                    "surface_hint": "qa_recheck",
                }

        # 3) If there are no messages at all → replan
        messages = state.get("messages", [])
        if not messages:
            return {
                "action": "replan",
                "reason": "no_messages",
                "surface_hint": "strategy_replan",
            }

        # 4) Default: accept
        return {
            "action": "accept",
            "reason": "default_accept",
            "surface_hint": "qa_recheck",
        }

# ============================================================
# From v10_8_delegation_policy.py
# ============================================================

def can_delegate(from_role: AgentRole, to_role: AgentRole) -> bool:
    """
    Deterministic fixed delegation policy.
    """
    if from_role == AgentRole.PLANNER:
        return to_role in {AgentRole.RETRIEVER, AgentRole.DRAFTER, AgentRole.QA}
    if from_role == AgentRole.RETRIEVER:
        return to_role == AgentRole.DRAFTER
    if from_role == AgentRole.DRAFTER:
        return to_role == AgentRole.QA
    if from_role == AgentRole.QA:
        return to_role == AgentRole.SAFETY
    return False


def delegation_metadata(sender: AgentRole, recipient: AgentRole) -> Dict[str, Any]:
    return {
        "from": sender.value,
        "to": recipient.value,
        "allowed": can_delegate(sender, recipient),
    }

# ============================================================
# From v10_8_council_voting.py
# ============================================================

def deterministic_vote(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Deterministic selection:
    - Highest score wins
    - Ties broken by smallest id
    """
    if not candidates:
        return {"id": None, "score": 0.0, "rationale": "no_candidates"}

    sorted_candidates = sorted(
        candidates,
        key=lambda c: (-float(c.get("score", 0.0)), int(c.get("id", 999999))),
    )
    return sorted_candidates[0]
