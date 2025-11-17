"""Layer 3 orchestration module consolidating DAG and orchestrators."""



from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from errors_controlflow import DAGValidationError
from node_result import NodeResult


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
"""Deterministic DAG execution engine for control-flow orchestrators."""

from copy import deepcopy
from typing import Any, Dict, List, Set

from errors_controlflow import NodeExecutionError
from node_result import NodeResult, NodeStatus


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
"""
L3 — Graph Orchestrator

Responsibilities:
    • Coordinate agentic workflows across a graph of tasks and dependencies.
    • Route intents from L1 reasoners to appropriate L2 execution agents.
    • Integrate safety decisions from L5 without embedding policy logic.

This file is scaffolded for Priority 0; implementation comes later.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from routing import run_model_for_plan
from observability import CostTracker
from l1_reasoning import StrategyReasoner
from l2_execution import RAGExecutionAgent
from l4_state import StateAdapter
from l5_safety import SafetyGateway
from node_result import NodeResult, NodeStatus
from self_correction import evaluate_correction
from self_correction import record_correction_event
from multi_agent import MultiAgentOrchestrator, AgentMessage, AgentRole, COUNCIL_OF_QA
from routing import RoutingCriteria, RoutingDecision, decide_route
from self_correction import SelfCorrectionSurface
from observability import record_event
from observability import compute_optimization_hint
from meta_profile import update_meta_profile_from_spans_and_self_correction
from utils_types import PlanObject, StatePatch


@dataclass
class OrchestrationResult:
    """Container describing the outcome of a single orchestration pass."""

    plan: PlanObject
    execution_patch: StatePatch
    safety_patch: StatePatch
    state: Dict[str, Any]


class GraphOrchestrator:
    """Coordinate planning, execution, patching, and safety evaluation."""

    def __init__(
        self,
        reasoner: StrategyReasoner | None = None,
        executor: RAGExecutionAgent | None = None,
        state_adapter: StateAdapter | None = None,
        safety_gateway: SafetyGateway | None = None,
    ) -> None:
        self.reasoner = reasoner or StrategyReasoner()
        self.executor = executor or RAGExecutionAgent()
        self.state_adapter = state_adapter or StateAdapter()
        self.safety_gateway = safety_gateway or SafetyGateway()
        self.cost_tracker = CostTracker()

    def orchestrate(
        self, state: Optional[Dict[str, Any]] = None, enable_multi_agent: bool = True
    ) -> OrchestrationResult:
        """Execute the deterministic orchestration sequence without side effects."""

        if state is not None:
            self.state_adapter.apply_patch(StatePatch(state))

        def run_plan(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            self.cost_tracker.start_span("planning")
            plan = self.reasoner.plan(current_state)
            self.cost_tracker.end_span("planning")
            plan["routing"] = {
                "complexity": "medium",
                "latency_target": 2.0,
                "cost_ceiling": 0.02,
                "risk_level": "normal",
            }
            routing_decision: RoutingDecision = decide_route(
                RoutingCriteria(
                    task_type="graph_orchestration",
                    complexity=str(plan["routing"].get("complexity", "low")),
                    latency_target_ms=int(plan["routing"].get("latency_target", 0) * 1000),
                    cost_ceiling_usd=float(plan["routing"].get("cost_ceiling", 0.0)),
                    risk_level=str(plan["routing"].get("risk_level", "normal")),
                )
            )
            plan["routing"]["selected_model"] = routing_decision.model
            return NodeResult(NodeStatus.SUCCESS, {"plan": plan})

        def run_execute(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            plan = context.get("plan")
            self.cost_tracker.start_span("execution")
            execution_patch = self.executor.execute(plan, current_state)
            self.cost_tracker.end_span("execution")
            return NodeResult(NodeStatus.SUCCESS, {"execution_patch": execution_patch})

        def run_patch(context: Dict[str, Any]) -> NodeResult:
            execution_patch = context.get("execution_patch")
            updated_state = self.state_adapter.apply_patch(execution_patch)
            return NodeResult(NodeStatus.SUCCESS, {"state": updated_state})

        def run_safety(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            plan = context.get("plan")
            payload = {
                "content": self._latest_content(current_state),
                "intent": plan,
                "context_tags": ["l3_orchestrator"],
            }
            safety_patch = self.safety_gateway.evaluate(payload)
            final_state = self.state_adapter.apply_patch(safety_patch)
            return NodeResult(
                NodeStatus.SUCCESS, {"safety_patch": safety_patch, "state": final_state}
            )

        dag = DAG(
            nodes={
                "plan_node": DAGNode(
                    name="plan_node",
                    run=run_plan,
                    condition=lambda ctx: bool(ctx.get("force_execute")),
                    conditional_edges={"condition_true": ["execute_node"]},
                ),
                "execute_node": DAGNode(
                    name="execute_node",
                    run=run_execute,
                    retries=1,
                ),
                "patch_node": DAGNode(
                    name="patch_node",
                    run=run_patch,
                    parallel=["safety_node"],
                ),
                "safety_node": DAGNode(name="safety_node", run=run_safety),
            },
            edges={
                "plan_node": ["execute_node"],
                "execute_node": ["patch_node"],
                "patch_node": ["safety_node"],
                "safety_node": [],
            },
        )

        executor = DAGExecutor()
        initial_context = {"state": self.state_adapter.state}
        final_context = executor.run(dag, initial_context)
        plan = final_context.get("plan", {})

        final_state = final_context.get("state", {})
        surface = SelfCorrectionSurface.STRATEGY_REPLAN
        recommendation = evaluate_correction(surface, final_state, final_context)
        record_correction_event(surface.value, recommendation, final_context.get("plan", {}))

        existing_self_correction = final_state.get("self_correction", {})
        if not isinstance(existing_self_correction, dict):
            existing_self_correction = {}
        existing_self_correction.update(
            {"surface": surface.value, "recommendation": recommendation}
        )
        final_state = self.state_adapter.apply_patch(
            StatePatch({"self_correction": existing_self_correction})
        )

        if enable_multi_agent:
            objective = plan.get("objective") if isinstance(plan, dict) else None
            msg = AgentMessage(
                sender=AgentRole.PLANNER,
                recipient=AgentRole.QA,
                content={"objective": objective},
                metadata={},
            )
            ma_orch = MultiAgentOrchestrator(
                graph=COUNCIL_OF_QA, state_adapter=self.state_adapter
            )
            ma_state = ma_orch.dispatch(msg, final_state)
            final_state = self.state_adapter.apply_patch(
                StatePatch({"multi_agent": ma_state.get("multi_agent")})
            )

        spans = self.cost_tracker.snapshot()
        ct_patch = StatePatch({"telemetry": spans})
        final_state = self.state_adapter.apply_patch(ct_patch)

        optimization = compute_optimization_hint(spans.get("spans", []))
        telemetry_block = final_state.get("telemetry", {})
        if not isinstance(telemetry_block, dict):
            telemetry_block = {}
        telemetry_block["optimization"] = optimization
        final_state = self.state_adapter.apply_patch(StatePatch({"telemetry": telemetry_block}))

        record_event(
            "orchestrator_cycle",
            {
                "plan_mode": plan.get("mode") if isinstance(plan, dict) else None,
                "spans": spans,
                "optimization": optimization,
            },
        )

        cache_patch = StatePatch(
            {
                "predictive_cache": {"snapshot": {}},
                "tuning": {"suggestion": {"temperature": 0.3, "max_tokens": 500}},
            }
        )
        final_state = self.state_adapter.apply_patch(cache_patch)

        predictive_cache = final_state.get("predictive_cache", {})
        if not isinstance(predictive_cache, dict):
            predictive_cache = {}
        predictive_cache["next_hint"] = optimization
        final_state = self.state_adapter.apply_patch(StatePatch({"predictive_cache": predictive_cache}))

        final_state["tooling_injection"] = {"cross_tool_reconciliation": True}

        model_data = run_model_for_plan(plan, final_state)
        final_state = self.state_adapter.apply_patch(StatePatch({"model_output": model_data}))

        self_correction_block = (
            final_state.get("self_correction") if isinstance(final_state, dict) else {}
        )
        if not isinstance(self_correction_block, dict):
            self_correction_block = {}
        update_meta_profile_from_spans_and_self_correction(
            spans.get("spans", []), self_correction_block
        )

        return OrchestrationResult(
            final_context.get("plan"),
            final_context.get("execution_patch"),
            final_context.get("safety_patch"),
            final_state,
        )

    @staticmethod
    def _latest_content(state: Dict[str, Any]) -> str:
        """Return the most recent assistant message for safety evaluation."""

        messages = state.get("messages") or []
        if messages:
            last = messages[-1]
            if isinstance(last, dict):
                return str(last.get("content", ""))
        return ""
"""
L3 — RAG Orchestrator

Responsibilities:
    • Manage control flow for retrieval-augmented reasoning cycles.
    • Align L1 RAG planning outputs with L2 retrieval execution steps.
    • Record orchestration outcomes for L4 state persistence and audits.

This file is scaffolded for Priority 0; implementation comes later.
"""

from typing import Any, Dict, Optional

from observability import CostTracker
from l1_reasoning import RAGReasoner
from l2_execution import RAGExecutionAgent
from l4_state import StateAdapter
from l5_safety import SafetyGateway
from node_result import NodeResult, NodeStatus
from self_correction import evaluate_correction
from self_correction import record_correction_event
from self_correction import SelfCorrectionSurface
from observability import record_event
from observability import compute_optimization_hint
from meta_profile import update_meta_profile_from_spans_and_self_correction
from utils_types import StatePatch


class RAGOrchestrator:
    """Manage the deterministic RAG orchestration sequence."""

    def __init__(
        self,
        reasoner: RAGReasoner | None = None,
        executor: RAGExecutionAgent | None = None,
        state_adapter: StateAdapter | None = None,
        safety_gateway: SafetyGateway | None = None,
    ) -> None:
        self.reasoner = reasoner or RAGReasoner()
        self.executor = executor or RAGExecutionAgent()
        self.state_adapter = state_adapter or StateAdapter()
        self.safety_gateway = safety_gateway or SafetyGateway()
        self.cost_tracker = CostTracker()

    def orchestrate(self, state: Optional[Dict[str, Any]] = None) -> OrchestrationResult:
        """Plan, execute, patch, and evaluate safety in order."""

        if state is not None:
            self.state_adapter.apply_patch(StatePatch(state))

        def run_plan(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            self.cost_tracker.start_span("planning")
            plan = self.reasoner.plan(current_state)
            self.cost_tracker.end_span("planning")
            plan["routing"] = {
                "complexity": "medium",
                "latency_target": 2.0,
                "cost_ceiling": 0.02,
                "risk_level": "normal",
            }
            return NodeResult(NodeStatus.SUCCESS, {"plan": plan})

        def run_execute(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            plan = context.get("plan")
            self.cost_tracker.start_span("execution")
            execution_patch = self.executor.execute(plan, current_state)
            self.cost_tracker.end_span("execution")
            return NodeResult(NodeStatus.SUCCESS, {"execution_patch": execution_patch})

        def run_patch(context: Dict[str, Any]) -> NodeResult:
            execution_patch = context.get("execution_patch")
            updated_state = self.state_adapter.apply_patch(execution_patch)
            return NodeResult(NodeStatus.SUCCESS, {"state": updated_state})

        def run_safety(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            plan = context.get("plan")
            payload = {
                "content": current_state.get("last_retrieval", {}),
                "intent": plan,
                "context_tags": ["l3_orchestrator"],
            }
            safety_patch = self.safety_gateway.evaluate(payload)
            final_state = self.state_adapter.apply_patch(safety_patch)
            return NodeResult(
                NodeStatus.SUCCESS, {"safety_patch": safety_patch, "state": final_state}
            )

        dag = DAG(
            nodes={
                "plan_node": DAGNode(
                    name="plan_node",
                    run=run_plan,
                    condition=lambda ctx: bool(ctx.get("force_execute")),
                    conditional_edges={"condition_true": ["execute_node"]},
                ),
                "execute_node": DAGNode(
                    name="execute_node",
                    run=run_execute,
                    fallback_edge="plan_node",
                    retries=1,
                ),
                "patch_node": DAGNode(
                    name="patch_node",
                    run=run_patch,
                    parallel=["safety_node"],
                ),
                "safety_node": DAGNode(name="safety_node", run=run_safety),
            },
            edges={
                "plan_node": ["execute_node"],
                "execute_node": ["patch_node"],
                "patch_node": ["safety_node"],
                "safety_node": [],
            },
        )

        executor = DAGExecutor()
        initial_context = {"state": self.state_adapter.state}
        final_context = executor.run(dag, initial_context)

        final_state = final_context.get("state", {})
        surface = SelfCorrectionSurface.RAG_RETRY
        recommendation = evaluate_correction(surface, final_state, final_context)
        record_correction_event(surface.value, recommendation, final_context.get("plan", {}))

        existing_self_correction = final_state.get("self_correction", {})
        if not isinstance(existing_self_correction, dict):
            existing_self_correction = {}
        existing_self_correction.update(
            {"surface": surface.value, "recommendation": recommendation}
        )
        final_state = self.state_adapter.apply_patch(
            StatePatch({"self_correction": existing_self_correction})
        )

        spans = self.cost_tracker.snapshot()
        ct_patch = StatePatch({"telemetry": spans})
        final_state = self.state_adapter.apply_patch(ct_patch)

        optimization = compute_optimization_hint(spans.get("spans", []))
        telemetry_block = final_state.get("telemetry", {})
        if not isinstance(telemetry_block, dict):
            telemetry_block = {}
        telemetry_block["optimization"] = optimization
        final_state = self.state_adapter.apply_patch(StatePatch({"telemetry": telemetry_block}))

        plan = final_context.get("plan", {})
        record_event(
            "orchestrator_cycle",
            {
                "plan_mode": plan.get("mode") if isinstance(plan, dict) else None,
                "spans": spans,
                "optimization": optimization,
            },
        )

        predictive_cache = final_state.get("predictive_cache", {})
        if not isinstance(predictive_cache, dict):
            predictive_cache = {}
        predictive_cache["next_hint"] = optimization
        final_state = self.state_adapter.apply_patch(StatePatch({"predictive_cache": predictive_cache}))

        self_correction_block = (
            final_state.get("self_correction") if isinstance(final_state, dict) else {}
        )
        if not isinstance(self_correction_block, dict):
            self_correction_block = {}
        update_meta_profile_from_spans_and_self_correction(
            spans.get("spans", []), self_correction_block
        )

        return OrchestrationResult(
            final_context.get("plan"),
            final_context.get("execution_patch"),
            final_context.get("safety_patch"),
            final_state,
        )
"""
L3 — Draft Orchestrator

Responsibilities:
    • Sequence drafting cycles driven by L1 drafting reasoners and L2 drafting execution agents.
    • Manage iteration checkpoints, handoffs, and validations.
    • Persist orchestration state via L4 mechanisms without embedding state logic directly.

This file is scaffolded for Priority 0; implementation comes later.
"""

from typing import Any, Dict, Optional

from observability import CostTracker
from l1_reasoning import DraftingReasoner
from l2_execution import DraftingExecutionAgent
from l4_state import StateAdapter
from l5_safety import SafetyGateway
from node_result import NodeResult, NodeStatus
from self_correction import evaluate_correction
from self_correction import record_correction_event
from self_correction import SelfCorrectionSurface
from observability import record_event
from observability import compute_optimization_hint
from meta_profile import update_meta_profile_from_spans_and_self_correction
from utils_types import StatePatch


class DraftOrchestrator:
    """Sequence drafting workflow steps via deterministic calls."""

    def __init__(
        self,
        reasoner: DraftingReasoner | None = None,
        executor: DraftingExecutionAgent | None = None,
        state_adapter: StateAdapter | None = None,
        safety_gateway: SafetyGateway | None = None,
    ) -> None:
        self.reasoner = reasoner or DraftingReasoner()
        self.executor = executor or DraftingExecutionAgent()
        self.state_adapter = state_adapter or StateAdapter()
        self.safety_gateway = safety_gateway or SafetyGateway()
        self.cost_tracker = CostTracker()

    def orchestrate(self, state: Optional[Dict[str, Any]] = None) -> OrchestrationResult:
        """Execute the L1→L2→L4→L5 drafting control flow."""

        if state is not None:
            self.state_adapter.apply_patch(StatePatch(state))

        def run_plan(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            self.cost_tracker.start_span("planning")
            plan = self.reasoner.plan(current_state)
            self.cost_tracker.end_span("planning")
            plan["routing"] = {
                "complexity": "medium",
                "latency_target": 2.0,
                "cost_ceiling": 0.02,
                "risk_level": "normal",
            }
            return NodeResult(NodeStatus.SUCCESS, {"plan": plan})

        def run_execute(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            plan = context.get("plan")
            self.cost_tracker.start_span("execution")
            execution_patch = self.executor.execute(plan, current_state)
            self.cost_tracker.end_span("execution")
            return NodeResult(NodeStatus.SUCCESS, {"execution_patch": execution_patch})

        def run_patch(context: Dict[str, Any]) -> NodeResult:
            execution_patch = context.get("execution_patch")
            updated_state = self.state_adapter.apply_patch(execution_patch)
            return NodeResult(NodeStatus.SUCCESS, {"state": updated_state})

        def run_safety(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            plan = context.get("plan")
            payload = {
                "content": current_state.get("draft", {}),
                "intent": plan,
                "context_tags": ["l3_orchestrator"],
            }
            safety_patch = self.safety_gateway.evaluate(payload)
            final_state = self.state_adapter.apply_patch(safety_patch)
            return NodeResult(
                NodeStatus.SUCCESS, {"safety_patch": safety_patch, "state": final_state}
            )

        dag = DAG(
            nodes={
                "plan_node": DAGNode(
                    name="plan_node",
                    run=run_plan,
                    condition=lambda ctx: bool(ctx.get("force_execute")),
                    conditional_edges={"condition_true": ["execute_node"]},
                ),
                "execute_node": DAGNode(
                    name="execute_node",
                    run=run_execute,
                    fallback_edge="plan_node",
                    retries=1,
                ),
                "patch_node": DAGNode(
                    name="patch_node",
                    run=run_patch,
                    parallel=["safety_node"],
                ),
                "safety_node": DAGNode(name="safety_node", run=run_safety),
            },
            edges={
                "plan_node": ["execute_node"],
                "execute_node": ["patch_node"],
                "patch_node": ["safety_node"],
                "safety_node": [],
            },
        )

        executor = DAGExecutor()
        initial_context = {"state": self.state_adapter.state}
        final_context = executor.run(dag, initial_context)

        final_state = final_context.get("state", {})
        surface = SelfCorrectionSurface.DRAFT_RETRY
        recommendation = evaluate_correction(surface, final_state, final_context)
        record_correction_event(surface.value, recommendation, final_context.get("plan", {}))

        existing_self_correction = final_state.get("self_correction", {})
        if not isinstance(existing_self_correction, dict):
            existing_self_correction = {}
        existing_self_correction.update(
            {"surface": surface.value, "recommendation": recommendation}
        )
        final_state = self.state_adapter.apply_patch(
            StatePatch({"self_correction": existing_self_correction})
        )

        spans = self.cost_tracker.snapshot()
        ct_patch = StatePatch({"telemetry": spans})
        final_state = self.state_adapter.apply_patch(ct_patch)

        optimization = compute_optimization_hint(spans.get("spans", []))
        telemetry_block = final_state.get("telemetry", {})
        if not isinstance(telemetry_block, dict):
            telemetry_block = {}
        telemetry_block["optimization"] = optimization
        final_state = self.state_adapter.apply_patch(StatePatch({"telemetry": telemetry_block}))

        plan = final_context.get("plan", {})
        record_event(
            "orchestrator_cycle",
            {
                "plan_mode": plan.get("mode") if isinstance(plan, dict) else None,
                "spans": spans,
                "optimization": optimization,
            },
        )

        predictive_cache = final_state.get("predictive_cache", {})
        if not isinstance(predictive_cache, dict):
            predictive_cache = {}
        predictive_cache["next_hint"] = optimization
        final_state = self.state_adapter.apply_patch(StatePatch({"predictive_cache": predictive_cache}))

        self_correction_block = (
            final_state.get("self_correction") if isinstance(final_state, dict) else {}
        )
        if not isinstance(self_correction_block, dict):
            self_correction_block = {}
        update_meta_profile_from_spans_and_self_correction(
            spans.get("spans", []), self_correction_block
        )

        return OrchestrationResult(
            final_context.get("plan"),
            final_context.get("execution_patch"),
            final_context.get("safety_patch"),
            final_state,
        )
"""
L3 — Bullet Orchestrator

Responsibilities:
    • Control bullet-generation workflows using L1 strategy outputs and L2 bullet executors.
    • Coordinate validation loops and format compliance steps.
    • Capture orchestration traces for L4 state and L5 safety reviews.

This file is scaffolded for Priority 0; implementation comes later.
"""

from typing import Any, Dict, Optional

from observability import CostTracker
from l1_reasoning import StrategyReasoner
from l2_execution import BulletExecutionAgent
from l4_state import StateAdapter
from l5_safety import SafetyGateway
from node_result import NodeResult, NodeStatus
from self_correction import evaluate_correction
from self_correction import record_correction_event
from self_correction import SelfCorrectionSurface
from observability import record_event
from observability import compute_optimization_hint
from meta_profile import update_meta_profile_from_spans_and_self_correction
from utils_types import StatePatch


class BulletOrchestrator:
    """Coordinate bullet generation without duplicating lower-layer logic."""

    def __init__(
        self,
        reasoner: StrategyReasoner | None = None,
        executor: BulletExecutionAgent | None = None,
        state_adapter: StateAdapter | None = None,
        safety_gateway: SafetyGateway | None = None,
    ) -> None:
        self.reasoner = reasoner or StrategyReasoner()
        self.executor = executor or BulletExecutionAgent()
        self.state_adapter = state_adapter or StateAdapter()
        self.safety_gateway = safety_gateway or SafetyGateway()
        self.cost_tracker = CostTracker()

    def orchestrate(self, state: Optional[Dict[str, Any]] = None) -> OrchestrationResult:
        """Run the deterministic orchestration sequence for bullet outputs."""

        if state is not None:
            self.state_adapter.apply_patch(StatePatch(state))

        def run_plan(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            self.cost_tracker.start_span("planning")
            plan = self.reasoner.plan(current_state)
            self.cost_tracker.end_span("planning")
            plan["routing"] = {
                "complexity": "medium",
                "latency_target": 2.0,
                "cost_ceiling": 0.02,
                "risk_level": "normal",
            }
            return NodeResult(NodeStatus.SUCCESS, {"plan": plan})

        def run_execute(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            plan = context.get("plan")
            self.cost_tracker.start_span("execution")
            execution_patch = self.executor.execute(plan, current_state)
            self.cost_tracker.end_span("execution")
            return NodeResult(NodeStatus.SUCCESS, {"execution_patch": execution_patch})

        def run_patch(context: Dict[str, Any]) -> NodeResult:
            execution_patch = context.get("execution_patch")
            updated_state = self.state_adapter.apply_patch(execution_patch)
            return NodeResult(NodeStatus.SUCCESS, {"state": updated_state})

        def run_safety(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            plan = context.get("plan")
            payload = {
                "content": current_state.get("messages", []),
                "intent": plan,
                "context_tags": ["l3_orchestrator"],
            }
            safety_patch = self.safety_gateway.evaluate(payload)
            final_state = self.state_adapter.apply_patch(safety_patch)
            return NodeResult(
                NodeStatus.SUCCESS, {"safety_patch": safety_patch, "state": final_state}
            )

        dag = DAG(
            nodes={
                "plan_node": DAGNode(
                    name="plan_node",
                    run=run_plan,
                    condition=lambda ctx: bool(ctx.get("force_execute")),
                    conditional_edges={"condition_true": ["execute_node"]},
                ),
                "execute_node": DAGNode(
                    name="execute_node",
                    run=run_execute,
                    fallback_edge="plan_node",
                    retries=1,
                ),
                "patch_node": DAGNode(
                    name="patch_node",
                    run=run_patch,
                    parallel=["safety_node"],
                ),
                "safety_node": DAGNode(name="safety_node", run=run_safety),
            },
            edges={
                "plan_node": ["execute_node"],
                "execute_node": ["patch_node"],
                "patch_node": ["safety_node"],
                "safety_node": [],
            },
        )

        executor = DAGExecutor()
        initial_context = {"state": self.state_adapter.state}
        final_context = executor.run(dag, initial_context)

        final_state = final_context.get("state", {})
        surface = SelfCorrectionSurface.STRATEGY_REPLAN
        recommendation = evaluate_correction(surface, final_state, final_context)
        record_correction_event(surface.value, recommendation, final_context.get("plan", {}))

        existing_self_correction = final_state.get("self_correction", {})
        if not isinstance(existing_self_correction, dict):
            existing_self_correction = {}
        existing_self_correction.update(
            {"surface": surface.value, "recommendation": recommendation}
        )
        final_state = self.state_adapter.apply_patch(
            StatePatch({"self_correction": existing_self_correction})
        )

        spans = self.cost_tracker.snapshot()
        ct_patch = StatePatch({"telemetry": spans})
        final_state = self.state_adapter.apply_patch(ct_patch)

        optimization = compute_optimization_hint(spans.get("spans", []))
        telemetry_block = final_state.get("telemetry", {})
        if not isinstance(telemetry_block, dict):
            telemetry_block = {}
        telemetry_block["optimization"] = optimization
        final_state = self.state_adapter.apply_patch(StatePatch({"telemetry": telemetry_block}))

        plan = final_context.get("plan", {})
        record_event(
            "orchestrator_cycle",
            {
                "plan_mode": plan.get("mode") if isinstance(plan, dict) else None,
                "spans": spans,
                "optimization": optimization,
            },
        )

        predictive_cache = final_state.get("predictive_cache", {})
        if not isinstance(predictive_cache, dict):
            predictive_cache = {}
        predictive_cache["next_hint"] = optimization
        final_state = self.state_adapter.apply_patch(StatePatch({"predictive_cache": predictive_cache}))

        self_correction_block = (
            final_state.get("self_correction") if isinstance(final_state, dict) else {}
        )
        if not isinstance(self_correction_block, dict):
            self_correction_block = {}
        update_meta_profile_from_spans_and_self_correction(
            spans.get("spans", []), self_correction_block
        )

        return OrchestrationResult(
            final_context.get("plan"),
            final_context.get("execution_patch"),
            final_context.get("safety_patch"),
            final_state,
        )
"""
L3 — QA Orchestrator

Responsibilities:
    • Govern validation workflows driven by L2 QA execution agents.
    • Align verification steps with L1 reasoning intents and L5 safety directives.
    • Aggregate validation artifacts into L4 state for traceability.

This file is scaffolded for Priority 0; implementation comes later.
"""

from typing import Any, Dict, Optional

from observability import CostTracker
from l1_reasoning import StrategyReasoner
from l2_execution import QAValidationAgent
from l4_state import StateAdapter
from l5_safety import SafetyGateway
from node_result import NodeResult, NodeStatus
from self_correction import ArbitrationEngine
from self_correction import evaluate_correction
from self_correction import record_correction_event
from self_correction import SelfCorrectionSurface
from observability import record_event
from observability import compute_optimization_hint
from meta_profile import update_meta_profile_from_spans_and_self_correction
from utils_types import StatePatch


class QAOrchestrator:
    """Govern QA validation without embedding lower-layer logic."""

    def __init__(
        self,
        reasoner: StrategyReasoner | None = None,
        executor: QAValidationAgent | None = None,
        state_adapter: StateAdapter | None = None,
        safety_gateway: SafetyGateway | None = None,
    ) -> None:
        self.reasoner = reasoner or StrategyReasoner()
        self.executor = executor or QAValidationAgent()
        self.state_adapter = state_adapter or StateAdapter()
        self.safety_gateway = safety_gateway or SafetyGateway()
        self.arbitration_engine = ArbitrationEngine()
        self.cost_tracker = CostTracker()

    def orchestrate(self, state: Optional[Dict[str, Any]] = None) -> OrchestrationResult:
        """Run plan→execute→patch→safety in order."""

        if state is not None:
            self.state_adapter.apply_patch(StatePatch(state))

        def run_plan(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            self.cost_tracker.start_span("planning")
            plan = self.reasoner.plan(current_state)
            self.cost_tracker.end_span("planning")
            plan["routing"] = {
                "complexity": "medium",
                "latency_target": 2.0,
                "cost_ceiling": 0.02,
                "risk_level": "normal",
            }
            return NodeResult(NodeStatus.SUCCESS, {"plan": plan})

        def run_execute(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            plan = context.get("plan")
            self.cost_tracker.start_span("execution")
            execution_patch = self.executor.execute(plan, current_state)
            self.cost_tracker.end_span("execution")
            return NodeResult(NodeStatus.SUCCESS, {"execution_patch": execution_patch})

        def run_patch(context: Dict[str, Any]) -> NodeResult:
            execution_patch = context.get("execution_patch")
            updated_state = self.state_adapter.apply_patch(execution_patch)
            return NodeResult(NodeStatus.SUCCESS, {"state": updated_state})

        def run_safety(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            plan = context.get("plan")
            payload = {
                "content": current_state.get("qa_report", {}),
                "intent": plan,
                "context_tags": ["l3_orchestrator"],
            }
            safety_patch = self.safety_gateway.evaluate(payload)
            final_state = self.state_adapter.apply_patch(safety_patch)
            return NodeResult(
                NodeStatus.SUCCESS, {"safety_patch": safety_patch, "state": final_state}
            )

        dag = DAG(
            nodes={
                "plan_node": DAGNode(
                    name="plan_node",
                    run=run_plan,
                    condition=lambda ctx: bool(ctx.get("force_execute")),
                    conditional_edges={"condition_true": ["execute_node"]},
                ),
                "execute_node": DAGNode(
                    name="execute_node",
                    run=run_execute,
                    fallback_edge="plan_node",
                    retries=1,
                ),
                "patch_node": DAGNode(
                    name="patch_node",
                    run=run_patch,
                    parallel=["safety_node"],
                ),
                "safety_node": DAGNode(name="safety_node", run=run_safety),
            },
            edges={
                "plan_node": ["execute_node"],
                "execute_node": ["patch_node"],
                "patch_node": ["safety_node"],
                "safety_node": [],
            },
        )

        executor = DAGExecutor()
        initial_context = {"state": self.state_adapter.state}
        final_context = executor.run(dag, initial_context)

        updated_state = final_context.get("state", {})
        safety_patch = final_context.get("safety_patch", StatePatch({}))
        execution_patch = final_context.get("execution_patch", StatePatch({}))
        qa_report = updated_state.get("qa_report", execution_patch.get("qa_report", {}))
        if not qa_report:
            qa_report = {"findings": [{"status": "pending"}]}
            execution_patch = StatePatch({"qa_report": qa_report})
        decision = self.arbitration_engine.evaluate(updated_state, qa_report, safety_patch)

        arbitration_patch: StatePatch = StatePatch(
            {
                "self_correction": {
                    "surface": SelfCorrectionSurface.QA_RECHECK.value,
                    "decision": decision,
                }
            }
        )
        final_state = self.state_adapter.apply_patch(arbitration_patch)

        surface = SelfCorrectionSurface.QA_RECHECK
        recommendation = evaluate_correction(surface, final_state, execution_patch)
        record_correction_event(surface.value, recommendation, final_context.get("plan", {}))

        self_correction = final_state.get("self_correction", {})
        if not isinstance(self_correction, dict):
            self_correction = {}
        self_correction.update(
            {
                "surface": surface.value,
                "decision": decision,
                "recommendation": recommendation,
            }
        )
        final_state = self.state_adapter.apply_patch(StatePatch({"self_correction": self_correction}))

        spans = self.cost_tracker.snapshot()
        ct_patch = StatePatch({"telemetry": spans})
        final_state = self.state_adapter.apply_patch(ct_patch)

        optimization = compute_optimization_hint(spans.get("spans", []))
        telemetry_block = final_state.get("telemetry", {})
        if not isinstance(telemetry_block, dict):
            telemetry_block = {}
        telemetry_block["optimization"] = optimization
        final_state = self.state_adapter.apply_patch(StatePatch({"telemetry": telemetry_block}))

        plan = final_context.get("plan", {})
        record_event(
            "orchestrator_cycle",
            {
                "plan_mode": plan.get("mode") if isinstance(plan, dict) else None,
                "spans": spans,
                "optimization": optimization,
            },
        )

        predictive_cache = final_state.get("predictive_cache", {})
        if not isinstance(predictive_cache, dict):
            predictive_cache = {}
        predictive_cache["next_hint"] = optimization
        final_state = self.state_adapter.apply_patch(StatePatch({"predictive_cache": predictive_cache}))

        self_correction_block = (
            final_state.get("self_correction") if isinstance(final_state, dict) else {}
        )
        if not isinstance(self_correction_block, dict):
            self_correction_block = {}
        update_meta_profile_from_spans_and_self_correction(
            spans.get("spans", []), self_correction_block
        )

        return OrchestrationResult(
            final_context.get("plan"),
            final_context.get("execution_patch"),
            final_context.get("safety_patch"),
            final_state,
        )
"""
L3 — Bullet Orchestrator

Responsibilities:
    • Control bullet-generation workflows using L1 strategy outputs and L2 bullet executors.
    • Coordinate validation loops and format compliance steps.
    • Capture orchestration traces for L4 state and L5 safety reviews.

This file is scaffolded for Priority 0; implementation comes later.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from l3_orchestration import DAGExecutor
from l3_orchestration import DAG, DAGNode
from observability import CostTracker
from l1_reasoning import StrategyReasoner
from l2_execution import BulletExecutionAgent
from l3_orchestration import OrchestrationResult
from l4_state import StateAdapter
from l5_safety import SafetyGateway
from node_result import NodeResult, NodeStatus
from self_correction import evaluate_correction
from self_correction import record_correction_event
from self_correction import SelfCorrectionSurface
from observability import record_event
from observability import compute_optimization_hint
from meta_profile import update_meta_profile_from_spans_and_self_correction
from utils_types import StatePatch


class BulletOrchestrator:
    """Coordinate bullet generation without duplicating lower-layer logic."""

    def __init__(
        self,
        reasoner: StrategyReasoner | None = None,
        executor: BulletExecutionAgent | None = None,
        state_adapter: StateAdapter | None = None,
        safety_gateway: SafetyGateway | None = None,
    ) -> None:
        self.reasoner = reasoner or StrategyReasoner()
        self.executor = executor or BulletExecutionAgent()
        self.state_adapter = state_adapter or StateAdapter()
        self.safety_gateway = safety_gateway or SafetyGateway()
        self.cost_tracker = CostTracker()

    def orchestrate(self, state: Optional[Dict[str, Any]] = None) -> OrchestrationResult:
        """Run the deterministic orchestration sequence for bullet outputs."""

        if state is not None:
            self.state_adapter.apply_patch(StatePatch(state))

        def run_plan(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            self.cost_tracker.start_span("planning")
            plan = self.reasoner.plan(current_state)
            self.cost_tracker.end_span("planning")
            plan["routing"] = {
                "complexity": "medium",
                "latency_target": 2.0,
                "cost_ceiling": 0.02,
                "risk_level": "normal",
            }
            return NodeResult(NodeStatus.SUCCESS, {"plan": plan})

        def run_execute(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            plan = context.get("plan")
            self.cost_tracker.start_span("execution")
            execution_patch = self.executor.execute(plan, current_state)
            self.cost_tracker.end_span("execution")
            return NodeResult(NodeStatus.SUCCESS, {"execution_patch": execution_patch})

        def run_patch(context: Dict[str, Any]) -> NodeResult:
            execution_patch = context.get("execution_patch")
            updated_state = self.state_adapter.apply_patch(execution_patch)
            return NodeResult(NodeStatus.SUCCESS, {"state": updated_state})

        def run_safety(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            plan = context.get("plan")
            payload = {
                "content": current_state.get("messages", []),
                "intent": plan,
                "context_tags": ["l3_orchestrator"],
            }
            safety_patch = self.safety_gateway.evaluate(payload)
            final_state = self.state_adapter.apply_patch(safety_patch)
            return NodeResult(
                NodeStatus.SUCCESS, {"safety_patch": safety_patch, "state": final_state}
            )

        dag = DAG(
            nodes={
                "plan_node": DAGNode(
                    name="plan_node",
                    run=run_plan,
                    condition=lambda ctx: bool(ctx.get("force_execute")),
                    conditional_edges={"condition_true": ["execute_node"]},
                ),
                "execute_node": DAGNode(
                    name="execute_node",
                    run=run_execute,
                    fallback_edge="plan_node",
                    retries=1,
                ),
                "patch_node": DAGNode(
                    name="patch_node",
                    run=run_patch,
                    parallel=["safety_node"],
                ),
                "safety_node": DAGNode(name="safety_node", run=run_safety),
            },
            edges={
                "plan_node": ["execute_node"],
                "execute_node": ["patch_node"],
                "patch_node": ["safety_node"],
                "safety_node": [],
            },
        )

        executor = DAGExecutor()
        initial_context = {"state": self.state_adapter.state}
        final_context = executor.run(dag, initial_context)

        final_state = final_context.get("state", {})
        surface = SelfCorrectionSurface.STRATEGY_REPLAN
        recommendation = evaluate_correction(surface, final_state, final_context)
        record_correction_event(surface.value, recommendation, final_context.get("plan", {}))

        existing_self_correction = final_state.get("self_correction", {})
        if not isinstance(existing_self_correction, dict):
            existing_self_correction = {}
        existing_self_correction.update(
            {"surface": surface.value, "recommendation": recommendation}
        )
        final_state = self.state_adapter.apply_patch(
            StatePatch({"self_correction": existing_self_correction})
        )

        spans = self.cost_tracker.snapshot()
        ct_patch = StatePatch({"telemetry": spans})
        final_state = self.state_adapter.apply_patch(ct_patch)

        optimization = compute_optimization_hint(spans.get("spans", []))
        telemetry_block = final_state.get("telemetry", {})
        if not isinstance(telemetry_block, dict):
            telemetry_block = {}
        telemetry_block["optimization"] = optimization
        final_state = self.state_adapter.apply_patch(StatePatch({"telemetry": telemetry_block}))

        plan = final_context.get("plan", {})
        record_event(
            "orchestrator_cycle",
            {
                "plan_mode": plan.get("mode") if isinstance(plan, dict) else None,
                "spans": spans,
                "optimization": optimization,
            },
        )

        predictive_cache = final_state.get("predictive_cache", {})
        if not isinstance(predictive_cache, dict):
            predictive_cache = {}
        predictive_cache["next_hint"] = optimization
        final_state = self.state_adapter.apply_patch(StatePatch({"predictive_cache": predictive_cache}))

        self_correction_block = (
            final_state.get("self_correction") if isinstance(final_state, dict) else {}
        )
        if not isinstance(self_correction_block, dict):
            self_correction_block = {}
        update_meta_profile_from_spans_and_self_correction(
            spans.get("spans", []), self_correction_block
        )

        return OrchestrationResult(
            final_context.get("plan"),
            final_context.get("execution_patch"),
            final_context.get("safety_patch"),
            final_state,
        )
"""
L3 — Draft Orchestrator

Responsibilities:
    • Sequence drafting cycles driven by L1 drafting reasoners and L2 drafting execution agents.
    • Manage iteration checkpoints, handoffs, and validations.
    • Persist orchestration state via L4 mechanisms without embedding state logic directly.

This file is scaffolded for Priority 0; implementation comes later.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from l3_orchestration import DAGExecutor
from l3_orchestration import DAG, DAGNode
from observability import CostTracker
from l1_reasoning import DraftingReasoner
from l2_execution import DraftingExecutionAgent
from l3_orchestration import OrchestrationResult
from l4_state import StateAdapter
from l5_safety import SafetyGateway
from node_result import NodeResult, NodeStatus
from self_correction import evaluate_correction
from self_correction import record_correction_event
from self_correction import SelfCorrectionSurface
from observability import record_event
from observability import compute_optimization_hint
from meta_profile import update_meta_profile_from_spans_and_self_correction
from utils_types import StatePatch


class DraftOrchestrator:
    """Sequence drafting workflow steps via deterministic calls."""

    def __init__(
        self,
        reasoner: DraftingReasoner | None = None,
        executor: DraftingExecutionAgent | None = None,
        state_adapter: StateAdapter | None = None,
        safety_gateway: SafetyGateway | None = None,
    ) -> None:
        self.reasoner = reasoner or DraftingReasoner()
        self.executor = executor or DraftingExecutionAgent()
        self.state_adapter = state_adapter or StateAdapter()
        self.safety_gateway = safety_gateway or SafetyGateway()
        self.cost_tracker = CostTracker()

    def orchestrate(self, state: Optional[Dict[str, Any]] = None) -> OrchestrationResult:
        """Execute the L1→L2→L4→L5 drafting control flow."""

        if state is not None:
            self.state_adapter.apply_patch(StatePatch(state))

        def run_plan(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            self.cost_tracker.start_span("planning")
            plan = self.reasoner.plan(current_state)
            self.cost_tracker.end_span("planning")
            plan["routing"] = {
                "complexity": "medium",
                "latency_target": 2.0,
                "cost_ceiling": 0.02,
                "risk_level": "normal",
            }
            return NodeResult(NodeStatus.SUCCESS, {"plan": plan})

        def run_execute(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            plan = context.get("plan")
            self.cost_tracker.start_span("execution")
            execution_patch = self.executor.execute(plan, current_state)
            self.cost_tracker.end_span("execution")
            return NodeResult(NodeStatus.SUCCESS, {"execution_patch": execution_patch})

        def run_patch(context: Dict[str, Any]) -> NodeResult:
            execution_patch = context.get("execution_patch")
            updated_state = self.state_adapter.apply_patch(execution_patch)
            return NodeResult(NodeStatus.SUCCESS, {"state": updated_state})

        def run_safety(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            plan = context.get("plan")
            payload = {
                "content": current_state.get("draft", {}),
                "intent": plan,
                "context_tags": ["l3_orchestrator"],
            }
            safety_patch = self.safety_gateway.evaluate(payload)
            final_state = self.state_adapter.apply_patch(safety_patch)
            return NodeResult(
                NodeStatus.SUCCESS, {"safety_patch": safety_patch, "state": final_state}
            )

        dag = DAG(
            nodes={
                "plan_node": DAGNode(
                    name="plan_node",
                    run=run_plan,
                    condition=lambda ctx: bool(ctx.get("force_execute")),
                    conditional_edges={"condition_true": ["execute_node"]},
                ),
                "execute_node": DAGNode(
                    name="execute_node",
                    run=run_execute,
                    fallback_edge="plan_node",
                    retries=1,
                ),
                "patch_node": DAGNode(
                    name="patch_node",
                    run=run_patch,
                    parallel=["safety_node"],
                ),
                "safety_node": DAGNode(name="safety_node", run=run_safety),
            },
            edges={
                "plan_node": ["execute_node"],
                "execute_node": ["patch_node"],
                "patch_node": ["safety_node"],
                "safety_node": [],
            },
        )

        executor = DAGExecutor()
        initial_context = {"state": self.state_adapter.state}
        final_context = executor.run(dag, initial_context)

        final_state = final_context.get("state", {})
        surface = SelfCorrectionSurface.DRAFT_RETRY
        recommendation = evaluate_correction(surface, final_state, final_context)
        record_correction_event(surface.value, recommendation, final_context.get("plan", {}))

        existing_self_correction = final_state.get("self_correction", {})
        if not isinstance(existing_self_correction, dict):
            existing_self_correction = {}
        existing_self_correction.update(
            {"surface": surface.value, "recommendation": recommendation}
        )
        final_state = self.state_adapter.apply_patch(
            StatePatch({"self_correction": existing_self_correction})
        )

        spans = self.cost_tracker.snapshot()
        ct_patch = StatePatch({"telemetry": spans})
        final_state = self.state_adapter.apply_patch(ct_patch)

        optimization = compute_optimization_hint(spans.get("spans", []))
        telemetry_block = final_state.get("telemetry", {})
        if not isinstance(telemetry_block, dict):
            telemetry_block = {}
        telemetry_block["optimization"] = optimization
        final_state = self.state_adapter.apply_patch(StatePatch({"telemetry": telemetry_block}))

        plan = final_context.get("plan", {})
        record_event(
            "orchestrator_cycle",
            {
                "plan_mode": plan.get("mode") if isinstance(plan, dict) else None,
                "spans": spans,
                "optimization": optimization,
            },
        )

        predictive_cache = final_state.get("predictive_cache", {})
        if not isinstance(predictive_cache, dict):
            predictive_cache = {}
        predictive_cache["next_hint"] = optimization
        final_state = self.state_adapter.apply_patch(StatePatch({"predictive_cache": predictive_cache}))

        self_correction_block = (
            final_state.get("self_correction") if isinstance(final_state, dict) else {}
        )
        if not isinstance(self_correction_block, dict):
            self_correction_block = {}
        update_meta_profile_from_spans_and_self_correction(
            spans.get("spans", []), self_correction_block
        )

        return OrchestrationResult(
            final_context.get("plan"),
            final_context.get("execution_patch"),
            final_context.get("safety_patch"),
            final_state,
        )
"""
L3 — RAG Orchestrator

Responsibilities:
    • Manage control flow for retrieval-augmented reasoning cycles.
    • Align L1 RAG planning outputs with L2 retrieval execution steps.
    • Record orchestration outcomes for L4 state persistence and audits.

This file is scaffolded for Priority 0; implementation comes later.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from l3_orchestration import DAGExecutor
from l3_orchestration import DAG, DAGNode
from observability import CostTracker
from l1_reasoning import RAGReasoner
from l2_execution import RAGExecutionAgent
from l3_orchestration import OrchestrationResult
from l4_state import StateAdapter
from l5_safety import SafetyGateway
from node_result import NodeResult, NodeStatus
from self_correction import evaluate_correction
from self_correction import record_correction_event
from self_correction import SelfCorrectionSurface
from observability import record_event
from observability import compute_optimization_hint
from meta_profile import update_meta_profile_from_spans_and_self_correction
from utils_types import StatePatch


class RAGOrchestrator:
    """Manage the deterministic RAG orchestration sequence."""

    def __init__(
        self,
        reasoner: RAGReasoner | None = None,
        executor: RAGExecutionAgent | None = None,
        state_adapter: StateAdapter | None = None,
        safety_gateway: SafetyGateway | None = None,
    ) -> None:
        self.reasoner = reasoner or RAGReasoner()
        self.executor = executor or RAGExecutionAgent()
        self.state_adapter = state_adapter or StateAdapter()
        self.safety_gateway = safety_gateway or SafetyGateway()
        self.cost_tracker = CostTracker()

    def orchestrate(self, state: Optional[Dict[str, Any]] = None) -> OrchestrationResult:
        """Plan, execute, patch, and evaluate safety in order."""

        if state is not None:
            self.state_adapter.apply_patch(StatePatch(state))

        def run_plan(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            self.cost_tracker.start_span("planning")
            plan = self.reasoner.plan(current_state)
            self.cost_tracker.end_span("planning")
            plan["routing"] = {
                "complexity": "medium",
                "latency_target": 2.0,
                "cost_ceiling": 0.02,
                "risk_level": "normal",
            }
            return NodeResult(NodeStatus.SUCCESS, {"plan": plan})

        def run_execute(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            plan = context.get("plan")
            self.cost_tracker.start_span("execution")
            execution_patch = self.executor.execute(plan, current_state)
            self.cost_tracker.end_span("execution")
            return NodeResult(NodeStatus.SUCCESS, {"execution_patch": execution_patch})

        def run_patch(context: Dict[str, Any]) -> NodeResult:
            execution_patch = context.get("execution_patch")
            updated_state = self.state_adapter.apply_patch(execution_patch)
            return NodeResult(NodeStatus.SUCCESS, {"state": updated_state})

        def run_safety(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            plan = context.get("plan")
            payload = {
                "content": current_state.get("last_retrieval", {}),
                "intent": plan,
                "context_tags": ["l3_orchestrator"],
            }
            safety_patch = self.safety_gateway.evaluate(payload)
            final_state = self.state_adapter.apply_patch(safety_patch)
            return NodeResult(
                NodeStatus.SUCCESS, {"safety_patch": safety_patch, "state": final_state}
            )

        dag = DAG(
            nodes={
                "plan_node": DAGNode(
                    name="plan_node",
                    run=run_plan,
                    condition=lambda ctx: bool(ctx.get("force_execute")),
                    conditional_edges={"condition_true": ["execute_node"]},
                ),
                "execute_node": DAGNode(
                    name="execute_node",
                    run=run_execute,
                    fallback_edge="plan_node",
                    retries=1,
                ),
                "patch_node": DAGNode(
                    name="patch_node",
                    run=run_patch,
                    parallel=["safety_node"],
                ),
                "safety_node": DAGNode(name="safety_node", run=run_safety),
            },
            edges={
                "plan_node": ["execute_node"],
                "execute_node": ["patch_node"],
                "patch_node": ["safety_node"],
                "safety_node": [],
            },
        )

        executor = DAGExecutor()
        initial_context = {"state": self.state_adapter.state}
        final_context = executor.run(dag, initial_context)

        final_state = final_context.get("state", {})
        surface = SelfCorrectionSurface.RAG_RETRY
        recommendation = evaluate_correction(surface, final_state, final_context)
        record_correction_event(surface.value, recommendation, final_context.get("plan", {}))

        existing_self_correction = final_state.get("self_correction", {})
        if not isinstance(existing_self_correction, dict):
            existing_self_correction = {}
        existing_self_correction.update(
            {"surface": surface.value, "recommendation": recommendation}
        )
        final_state = self.state_adapter.apply_patch(
            StatePatch({"self_correction": existing_self_correction})
        )

        spans = self.cost_tracker.snapshot()
        ct_patch = StatePatch({"telemetry": spans})
        final_state = self.state_adapter.apply_patch(ct_patch)

        optimization = compute_optimization_hint(spans.get("spans", []))
        telemetry_block = final_state.get("telemetry", {})
        if not isinstance(telemetry_block, dict):
            telemetry_block = {}
        telemetry_block["optimization"] = optimization
        final_state = self.state_adapter.apply_patch(StatePatch({"telemetry": telemetry_block}))

        plan = final_context.get("plan", {})
        record_event(
            "orchestrator_cycle",
            {
                "plan_mode": plan.get("mode") if isinstance(plan, dict) else None,
                "spans": spans,
                "optimization": optimization,
            },
        )

        predictive_cache = final_state.get("predictive_cache", {})
        if not isinstance(predictive_cache, dict):
            predictive_cache = {}
        predictive_cache["next_hint"] = optimization
        final_state = self.state_adapter.apply_patch(StatePatch({"predictive_cache": predictive_cache}))

        self_correction_block = (
            final_state.get("self_correction") if isinstance(final_state, dict) else {}
        )
        if not isinstance(self_correction_block, dict):
            self_correction_block = {}
        update_meta_profile_from_spans_and_self_correction(
            spans.get("spans", []), self_correction_block
        )

        return OrchestrationResult(
            final_context.get("plan"),
            final_context.get("execution_patch"),
            final_context.get("safety_patch"),
            final_state,
        )
"""Local orchestrator for RAG planning and execution."""
from __future__ import annotations

from typing import Any, Dict, Optional

from rag_planning import RAGPlanningStack
from rag_execution import RAGExecutionStack


class RAGOrchestratorStack:
    """Runs planning then execution for retrieval tasks."""

    def __init__(self):
        self.planner = RAGPlanningStack()
        self.executor = RAGExecutionStack()

    async def run_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        plan_patch = await self.planner.run_async(state, workflow_id)
        interim_state = {**state, **plan_patch}
        exec_patch = await self.executor.run_async(interim_state, workflow_id)
        final_state = {**interim_state, **exec_patch}
        return final_state
"""Multi-agent module consolidating messaging and orchestration logic."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class AgentMessage:
    sender: AgentRole
    recipient: AgentRole
    content: Dict[str, Any]
    metadata: Dict[str, Any]


def route_to_specialist(graph, message: AgentMessage):
    """
    Deterministic routing:
    - Finds first node whose role matches message.recipient.
    - No execution, no side effects.
    """
    for node in graph.nodes:
        if node.role == message.recipient:
            metadata = message.metadata if message.metadata is not None else {}
            metadata["route_trace"] = [message.sender.value, node.role.value]
            message.metadata = metadata
            return node
    return None
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any


class AgentRole(str, Enum):
    PLANNER = "planner"
    RETRIEVER = "retriever"
    DRAFTER = "drafter"
    BULLET = "bullet"
    QA = "qa"
    SAFETY = "safety"


@dataclass
class AgentNode:
    role: AgentRole
    config: Dict[str, Any]


@dataclass
class AgentGraph:
    nodes: List[AgentNode]
    edges: List[tuple]  # (from_role, to_role)


LINEAR_PIPELINE = AgentGraph(
    nodes=[
        AgentNode(AgentRole.PLANNER, {}),
        AgentNode(AgentRole.RETRIEVER, {}),
        AgentNode(AgentRole.DRAFTER, {}),
        AgentNode(AgentRole.QA, {}),
        AgentNode(AgentRole.SAFETY, {}),
    ],
    edges=[
        (AgentRole.PLANNER, AgentRole.RETRIEVER),
        (AgentRole.RETRIEVER, AgentRole.DRAFTER),
        (AgentRole.DRAFTER, AgentRole.QA),
        (AgentRole.QA, AgentRole.SAFETY),
    ],
)


COUNCIL_OF_QA = AgentGraph(
    nodes=[
        AgentNode(AgentRole.QA, {"id": 1}),
        AgentNode(AgentRole.QA, {"id": 2}),
        AgentNode(AgentRole.QA, {"id": 3}),
    ],
    edges=[],
)


def summarize_graph(graph):
    """
    Deterministic summary of graph nodes and edges.
    """
    def _role_value(entry):
        return entry.role.value if hasattr(entry, "role") else entry.value

    return {
        "nodes": [_role_value(n) for n in graph.nodes],
        "edges": [(_role_value(a), _role_value(b)) for (a, b) in graph.edges],
    }
from typing import Dict, Any


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
from typing import List, Dict, Any


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
from typing import Dict, Any

from utils_types import StatePatch


class MultiAgentOrchestrator:
    def __init__(self, graph: AgentGraph, state_adapter):
        self.graph = graph
        self.state_adapter = state_adapter

    def dispatch(self, message: AgentMessage, state: Dict[str, Any]) -> Dict[str, Any]:
        recipient_node = route_to_specialist(self.graph, message)
        recipient = recipient_node.role if recipient_node else None

        multi_agent_block: Dict[str, Any] = {
            "last_message": {
                "content": message.content,
                "sender": message.sender.value,
                "recipient": message.recipient.value,
            },
            "sender": message.sender.value,
            "recipient": recipient.value if recipient else None,
            "routed_to": recipient.value if recipient else None,
            "delegation": delegation_metadata(message.sender, recipient) if recipient else None,
            "graph_summary": summarize_graph(self.graph),
        }

        if self.graph == COUNCIL_OF_QA:
            multi_agent_block["council_vote"] = deterministic_vote(
                [
                    {"id": 1, "score": 0.70, "rationale": "baseline"},
                    {"id": 2, "score": 0.70, "rationale": "alt"},
                ]
            )

        patch = StatePatch({"multi_agent": multi_agent_block})
        return self.state_adapter.apply_patch(patch)
"""Layer 3 orchestration module consolidating DAG and orchestrators."""



from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from errors_controlflow import DAGValidationError
from node_result import NodeResult


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
"""Deterministic DAG execution engine for control-flow orchestrators."""

from copy import deepcopy
from typing import Any, Dict, List, Set

from errors_controlflow import NodeExecutionError
from node_result import NodeResult, NodeStatus


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
"""
L3 — Graph Orchestrator

Responsibilities:
    • Coordinate agentic workflows across a graph of tasks and dependencies.
    • Route intents from L1 reasoners to appropriate L2 execution agents.
    • Integrate safety decisions from L5 without embedding policy logic.

This file is scaffolded for Priority 0; implementation comes later.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from routing import run_model_for_plan
from observability import CostTracker
from l1_reasoning import StrategyReasoner
from l2_execution import RAGExecutionAgent
from l4_state import StateAdapter
from l5_safety import SafetyGateway
from node_result import NodeResult, NodeStatus
from self_correction import evaluate_correction
from self_correction import record_correction_event
from multi_agent import MultiAgentOrchestrator, AgentMessage, AgentRole, COUNCIL_OF_QA
from routing import RoutingCriteria, RoutingDecision, decide_route
from self_correction import SelfCorrectionSurface
from observability import record_event
from observability import compute_optimization_hint
from meta_profile import update_meta_profile_from_spans_and_self_correction
from utils_types import PlanObject, StatePatch


@dataclass
class OrchestrationResult:
    """Container describing the outcome of a single orchestration pass."""

    plan: PlanObject
    execution_patch: StatePatch
    safety_patch: StatePatch
    state: Dict[str, Any]


class GraphOrchestrator:
    """Coordinate planning, execution, patching, and safety evaluation."""

    def __init__(
        self,
        reasoner: StrategyReasoner | None = None,
        executor: RAGExecutionAgent | None = None,
        state_adapter: StateAdapter | None = None,
        safety_gateway: SafetyGateway | None = None,
    ) -> None:
        self.reasoner = reasoner or StrategyReasoner()
        self.executor = executor or RAGExecutionAgent()
        self.state_adapter = state_adapter or StateAdapter()
        self.safety_gateway = safety_gateway or SafetyGateway()
        self.cost_tracker = CostTracker()

    def orchestrate(
        self, state: Optional[Dict[str, Any]] = None, enable_multi_agent: bool = True
    ) -> OrchestrationResult:
        """Execute the deterministic orchestration sequence without side effects."""

        if state is not None:
            self.state_adapter.apply_patch(StatePatch(state))

        def run_plan(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            self.cost_tracker.start_span("planning")
            plan = self.reasoner.plan(current_state)
            self.cost_tracker.end_span("planning")
            plan["routing"] = {
                "complexity": "medium",
                "latency_target": 2.0,
                "cost_ceiling": 0.02,
                "risk_level": "normal",
            }
            routing_decision: RoutingDecision = decide_route(
                RoutingCriteria(
                    task_type="graph_orchestration",
                    complexity=str(plan["routing"].get("complexity", "low")),
                    latency_target_ms=int(plan["routing"].get("latency_target", 0) * 1000),
                    cost_ceiling_usd=float(plan["routing"].get("cost_ceiling", 0.0)),
                    risk_level=str(plan["routing"].get("risk_level", "normal")),
                )
            )
            plan["routing"]["selected_model"] = routing_decision.model
            return NodeResult(NodeStatus.SUCCESS, {"plan": plan})

        def run_execute(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            plan = context.get("plan")
            self.cost_tracker.start_span("execution")
            execution_patch = self.executor.execute(plan, current_state)
            self.cost_tracker.end_span("execution")
            return NodeResult(NodeStatus.SUCCESS, {"execution_patch": execution_patch})

        def run_patch(context: Dict[str, Any]) -> NodeResult:
            execution_patch = context.get("execution_patch")
            updated_state = self.state_adapter.apply_patch(execution_patch)
            return NodeResult(NodeStatus.SUCCESS, {"state": updated_state})

        def run_safety(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            plan = context.get("plan")
            payload = {
                "content": self._latest_content(current_state),
                "intent": plan,
                "context_tags": ["l3_orchestrator"],
            }
            safety_patch = self.safety_gateway.evaluate(payload)
            final_state = self.state_adapter.apply_patch(safety_patch)
            return NodeResult(
                NodeStatus.SUCCESS, {"safety_patch": safety_patch, "state": final_state}
            )

        dag = DAG(
            nodes={
                "plan_node": DAGNode(
                    name="plan_node",
                    run=run_plan,
                    condition=lambda ctx: bool(ctx.get("force_execute")),
                    conditional_edges={"condition_true": ["execute_node"]},
                ),
                "execute_node": DAGNode(
                    name="execute_node",
                    run=run_execute,
                    retries=1,
                ),
                "patch_node": DAGNode(
                    name="patch_node",
                    run=run_patch,
                    parallel=["safety_node"],
                ),
                "safety_node": DAGNode(name="safety_node", run=run_safety),
            },
            edges={
                "plan_node": ["execute_node"],
                "execute_node": ["patch_node"],
                "patch_node": ["safety_node"],
                "safety_node": [],
            },
        )

        executor = DAGExecutor()
        initial_context = {"state": self.state_adapter.state}
        final_context = executor.run(dag, initial_context)
        plan = final_context.get("plan", {})

        final_state = final_context.get("state", {})
        surface = SelfCorrectionSurface.STRATEGY_REPLAN
        recommendation = evaluate_correction(surface, final_state, final_context)
        record_correction_event(surface.value, recommendation, final_context.get("plan", {}))

        existing_self_correction = final_state.get("self_correction", {})
        if not isinstance(existing_self_correction, dict):
            existing_self_correction = {}
        existing_self_correction.update(
            {"surface": surface.value, "recommendation": recommendation}
        )
        final_state = self.state_adapter.apply_patch(
            StatePatch({"self_correction": existing_self_correction})
        )

        if enable_multi_agent:
            objective = plan.get("objective") if isinstance(plan, dict) else None
            msg = AgentMessage(
                sender=AgentRole.PLANNER,
                recipient=AgentRole.QA,
                content={"objective": objective},
                metadata={},
            )
            ma_orch = MultiAgentOrchestrator(
                graph=COUNCIL_OF_QA, state_adapter=self.state_adapter
            )
            ma_state = ma_orch.dispatch(msg, final_state)
            final_state = self.state_adapter.apply_patch(
                StatePatch({"multi_agent": ma_state.get("multi_agent")})
            )

        spans = self.cost_tracker.snapshot()
        ct_patch = StatePatch({"telemetry": spans})
        final_state = self.state_adapter.apply_patch(ct_patch)

        optimization = compute_optimization_hint(spans.get("spans", []))
        telemetry_block = final_state.get("telemetry", {})
        if not isinstance(telemetry_block, dict):
            telemetry_block = {}
        telemetry_block["optimization"] = optimization
        final_state = self.state_adapter.apply_patch(StatePatch({"telemetry": telemetry_block}))

        record_event(
            "orchestrator_cycle",
            {
                "plan_mode": plan.get("mode") if isinstance(plan, dict) else None,
                "spans": spans,
                "optimization": optimization,
            },
        )

        cache_patch = StatePatch(
            {
                "predictive_cache": {"snapshot": {}},
                "tuning": {"suggestion": {"temperature": 0.3, "max_tokens": 500}},
            }
        )
        final_state = self.state_adapter.apply_patch(cache_patch)

        predictive_cache = final_state.get("predictive_cache", {})
        if not isinstance(predictive_cache, dict):
            predictive_cache = {}
        predictive_cache["next_hint"] = optimization
        final_state = self.state_adapter.apply_patch(StatePatch({"predictive_cache": predictive_cache}))

        final_state["tooling_injection"] = {"cross_tool_reconciliation": True}

        model_data = run_model_for_plan(plan, final_state)
        final_state = self.state_adapter.apply_patch(StatePatch({"model_output": model_data}))

        self_correction_block = (
            final_state.get("self_correction") if isinstance(final_state, dict) else {}
        )
        if not isinstance(self_correction_block, dict):
            self_correction_block = {}
        update_meta_profile_from_spans_and_self_correction(
            spans.get("spans", []), self_correction_block
        )

        return OrchestrationResult(
            final_context.get("plan"),
            final_context.get("execution_patch"),
            final_context.get("safety_patch"),
            final_state,
        )

    @staticmethod
    def _latest_content(state: Dict[str, Any]) -> str:
        """Return the most recent assistant message for safety evaluation."""

        messages = state.get("messages") or []
        if messages:
            last = messages[-1]
            if isinstance(last, dict):
                return str(last.get("content", ""))
        return ""
"""
L3 — RAG Orchestrator

Responsibilities:
    • Manage control flow for retrieval-augmented reasoning cycles.
    • Align L1 RAG planning outputs with L2 retrieval execution steps.
    • Record orchestration outcomes for L4 state persistence and audits.

This file is scaffolded for Priority 0; implementation comes later.
"""

from typing import Any, Dict, Optional

from observability import CostTracker
from l1_reasoning import RAGReasoner
from l2_execution import RAGExecutionAgent
from l4_state import StateAdapter
from l5_safety import SafetyGateway
from node_result import NodeResult, NodeStatus
from self_correction import evaluate_correction
from self_correction import record_correction_event
from self_correction import SelfCorrectionSurface
from observability import record_event
from observability import compute_optimization_hint
from meta_profile import update_meta_profile_from_spans_and_self_correction
from utils_types import StatePatch


class RAGOrchestrator:
    """Manage the deterministic RAG orchestration sequence."""

    def __init__(
        self,
        reasoner: RAGReasoner | None = None,
        executor: RAGExecutionAgent | None = None,
        state_adapter: StateAdapter | None = None,
        safety_gateway: SafetyGateway | None = None,
    ) -> None:
        self.reasoner = reasoner or RAGReasoner()
        self.executor = executor or RAGExecutionAgent()
        self.state_adapter = state_adapter or StateAdapter()
        self.safety_gateway = safety_gateway or SafetyGateway()
        self.cost_tracker = CostTracker()

    def orchestrate(self, state: Optional[Dict[str, Any]] = None) -> OrchestrationResult:
        """Plan, execute, patch, and evaluate safety in order."""

        if state is not None:
            self.state_adapter.apply_patch(StatePatch(state))

        def run_plan(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            self.cost_tracker.start_span("planning")
            plan = self.reasoner.plan(current_state)
            self.cost_tracker.end_span("planning")
            plan["routing"] = {
                "complexity": "medium",
                "latency_target": 2.0,
                "cost_ceiling": 0.02,
                "risk_level": "normal",
            }
            return NodeResult(NodeStatus.SUCCESS, {"plan": plan})

        def run_execute(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            plan = context.get("plan")
            self.cost_tracker.start_span("execution")
            execution_patch = self.executor.execute(plan, current_state)
            self.cost_tracker.end_span("execution")
            return NodeResult(NodeStatus.SUCCESS, {"execution_patch": execution_patch})

        def run_patch(context: Dict[str, Any]) -> NodeResult:
            execution_patch = context.get("execution_patch")
            updated_state = self.state_adapter.apply_patch(execution_patch)
            return NodeResult(NodeStatus.SUCCESS, {"state": updated_state})

        def run_safety(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            plan = context.get("plan")
            payload = {
                "content": current_state.get("last_retrieval", {}),
                "intent": plan,
                "context_tags": ["l3_orchestrator"],
            }
            safety_patch = self.safety_gateway.evaluate(payload)
            final_state = self.state_adapter.apply_patch(safety_patch)
            return NodeResult(
                NodeStatus.SUCCESS, {"safety_patch": safety_patch, "state": final_state}
            )

        dag = DAG(
            nodes={
                "plan_node": DAGNode(
                    name="plan_node",
                    run=run_plan,
                    condition=lambda ctx: bool(ctx.get("force_execute")),
                    conditional_edges={"condition_true": ["execute_node"]},
                ),
                "execute_node": DAGNode(
                    name="execute_node",
                    run=run_execute,
                    fallback_edge="plan_node",
                    retries=1,
                ),
                "patch_node": DAGNode(
                    name="patch_node",
                    run=run_patch,
                    parallel=["safety_node"],
                ),
                "safety_node": DAGNode(name="safety_node", run=run_safety),
            },
            edges={
                "plan_node": ["execute_node"],
                "execute_node": ["patch_node"],
                "patch_node": ["safety_node"],
                "safety_node": [],
            },
        )

        executor = DAGExecutor()
        initial_context = {"state": self.state_adapter.state}
        final_context = executor.run(dag, initial_context)

        final_state = final_context.get("state", {})
        surface = SelfCorrectionSurface.RAG_RETRY
        recommendation = evaluate_correction(surface, final_state, final_context)
        record_correction_event(surface.value, recommendation, final_context.get("plan", {}))

        existing_self_correction = final_state.get("self_correction", {})
        if not isinstance(existing_self_correction, dict):
            existing_self_correction = {}
        existing_self_correction.update(
            {"surface": surface.value, "recommendation": recommendation}
        )
        final_state = self.state_adapter.apply_patch(
            StatePatch({"self_correction": existing_self_correction})
        )

        spans = self.cost_tracker.snapshot()
        ct_patch = StatePatch({"telemetry": spans})
        final_state = self.state_adapter.apply_patch(ct_patch)

        optimization = compute_optimization_hint(spans.get("spans", []))
        telemetry_block = final_state.get("telemetry", {})
        if not isinstance(telemetry_block, dict):
            telemetry_block = {}
        telemetry_block["optimization"] = optimization
        final_state = self.state_adapter.apply_patch(StatePatch({"telemetry": telemetry_block}))

        plan = final_context.get("plan", {})
        record_event(
            "orchestrator_cycle",
            {
                "plan_mode": plan.get("mode") if isinstance(plan, dict) else None,
                "spans": spans,
                "optimization": optimization,
            },
        )

        predictive_cache = final_state.get("predictive_cache", {})
        if not isinstance(predictive_cache, dict):
            predictive_cache = {}
        predictive_cache["next_hint"] = optimization
        final_state = self.state_adapter.apply_patch(StatePatch({"predictive_cache": predictive_cache}))

        self_correction_block = (
            final_state.get("self_correction") if isinstance(final_state, dict) else {}
        )
        if not isinstance(self_correction_block, dict):
            self_correction_block = {}
        update_meta_profile_from_spans_and_self_correction(
            spans.get("spans", []), self_correction_block
        )

        return OrchestrationResult(
            final_context.get("plan"),
            final_context.get("execution_patch"),
            final_context.get("safety_patch"),
            final_state,
        )
"""
L3 — Draft Orchestrator

Responsibilities:
    • Sequence drafting cycles driven by L1 drafting reasoners and L2 drafting execution agents.
    • Manage iteration checkpoints, handoffs, and validations.
    • Persist orchestration state via L4 mechanisms without embedding state logic directly.

This file is scaffolded for Priority 0; implementation comes later.
"""

from typing import Any, Dict, Optional

from observability import CostTracker
from l1_reasoning import DraftingReasoner
from l2_execution import DraftingExecutionAgent
from l4_state import StateAdapter
from l5_safety import SafetyGateway
from node_result import NodeResult, NodeStatus
from self_correction import evaluate_correction
from self_correction import record_correction_event
from self_correction import SelfCorrectionSurface
from observability import record_event
from observability import compute_optimization_hint
from meta_profile import update_meta_profile_from_spans_and_self_correction
from utils_types import StatePatch


class DraftOrchestrator:
    """Sequence drafting workflow steps via deterministic calls."""

    def __init__(
        self,
        reasoner: DraftingReasoner | None = None,
        executor: DraftingExecutionAgent | None = None,
        state_adapter: StateAdapter | None = None,
        safety_gateway: SafetyGateway | None = None,
    ) -> None:
        self.reasoner = reasoner or DraftingReasoner()
        self.executor = executor or DraftingExecutionAgent()
        self.state_adapter = state_adapter or StateAdapter()
        self.safety_gateway = safety_gateway or SafetyGateway()
        self.cost_tracker = CostTracker()

    def orchestrate(self, state: Optional[Dict[str, Any]] = None) -> OrchestrationResult:
        """Execute the L1→L2→L4→L5 drafting control flow."""

        if state is not None:
            self.state_adapter.apply_patch(StatePatch(state))

        def run_plan(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            self.cost_tracker.start_span("planning")
            plan = self.reasoner.plan(current_state)
            self.cost_tracker.end_span("planning")
            plan["routing"] = {
                "complexity": "medium",
                "latency_target": 2.0,
                "cost_ceiling": 0.02,
                "risk_level": "normal",
            }
            return NodeResult(NodeStatus.SUCCESS, {"plan": plan})

        def run_execute(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            plan = context.get("plan")
            self.cost_tracker.start_span("execution")
            execution_patch = self.executor.execute(plan, current_state)
            self.cost_tracker.end_span("execution")
            return NodeResult(NodeStatus.SUCCESS, {"execution_patch": execution_patch})

        def run_patch(context: Dict[str, Any]) -> NodeResult:
            execution_patch = context.get("execution_patch")
            updated_state = self.state_adapter.apply_patch(execution_patch)
            return NodeResult(NodeStatus.SUCCESS, {"state": updated_state})

        def run_safety(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            plan = context.get("plan")
            payload = {
                "content": current_state.get("draft", {}),
                "intent": plan,
                "context_tags": ["l3_orchestrator"],
            }
            safety_patch = self.safety_gateway.evaluate(payload)
            final_state = self.state_adapter.apply_patch(safety_patch)
            return NodeResult(
                NodeStatus.SUCCESS, {"safety_patch": safety_patch, "state": final_state}
            )

        dag = DAG(
            nodes={
                "plan_node": DAGNode(
                    name="plan_node",
                    run=run_plan,
                    condition=lambda ctx: bool(ctx.get("force_execute")),
                    conditional_edges={"condition_true": ["execute_node"]},
                ),
                "execute_node": DAGNode(
                    name="execute_node",
                    run=run_execute,
                    fallback_edge="plan_node",
                    retries=1,
                ),
                "patch_node": DAGNode(
                    name="patch_node",
                    run=run_patch,
                    parallel=["safety_node"],
                ),
                "safety_node": DAGNode(name="safety_node", run=run_safety),
            },
            edges={
                "plan_node": ["execute_node"],
                "execute_node": ["patch_node"],
                "patch_node": ["safety_node"],
                "safety_node": [],
            },
        )

        executor = DAGExecutor()
        initial_context = {"state": self.state_adapter.state}
        final_context = executor.run(dag, initial_context)

        final_state = final_context.get("state", {})
        surface = SelfCorrectionSurface.DRAFT_RETRY
        recommendation = evaluate_correction(surface, final_state, final_context)
        record_correction_event(surface.value, recommendation, final_context.get("plan", {}))

        existing_self_correction = final_state.get("self_correction", {})
        if not isinstance(existing_self_correction, dict):
            existing_self_correction = {}
        existing_self_correction.update(
            {"surface": surface.value, "recommendation": recommendation}
        )
        final_state = self.state_adapter.apply_patch(
            StatePatch({"self_correction": existing_self_correction})
        )

        spans = self.cost_tracker.snapshot()
        ct_patch = StatePatch({"telemetry": spans})
        final_state = self.state_adapter.apply_patch(ct_patch)

        optimization = compute_optimization_hint(spans.get("spans", []))
        telemetry_block = final_state.get("telemetry", {})
        if not isinstance(telemetry_block, dict):
            telemetry_block = {}
        telemetry_block["optimization"] = optimization
        final_state = self.state_adapter.apply_patch(StatePatch({"telemetry": telemetry_block}))

        plan = final_context.get("plan", {})
        record_event(
            "orchestrator_cycle",
            {
                "plan_mode": plan.get("mode") if isinstance(plan, dict) else None,
                "spans": spans,
                "optimization": optimization,
            },
        )

        predictive_cache = final_state.get("predictive_cache", {})
        if not isinstance(predictive_cache, dict):
            predictive_cache = {}
        predictive_cache["next_hint"] = optimization
        final_state = self.state_adapter.apply_patch(StatePatch({"predictive_cache": predictive_cache}))

        self_correction_block = (
            final_state.get("self_correction") if isinstance(final_state, dict) else {}
        )
        if not isinstance(self_correction_block, dict):
            self_correction_block = {}
        update_meta_profile_from_spans_and_self_correction(
            spans.get("spans", []), self_correction_block
        )

        return OrchestrationResult(
            final_context.get("plan"),
            final_context.get("execution_patch"),
            final_context.get("safety_patch"),
            final_state,
        )
"""
L3 — Bullet Orchestrator

Responsibilities:
    • Control bullet-generation workflows using L1 strategy outputs and L2 bullet executors.
    • Coordinate validation loops and format compliance steps.
    • Capture orchestration traces for L4 state and L5 safety reviews.

This file is scaffolded for Priority 0; implementation comes later.
"""

from typing import Any, Dict, Optional

from observability import CostTracker
from l1_reasoning import StrategyReasoner
from l2_execution import BulletExecutionAgent
from l4_state import StateAdapter
from l5_safety import SafetyGateway
from node_result import NodeResult, NodeStatus
from self_correction import evaluate_correction
from self_correction import record_correction_event
from self_correction import SelfCorrectionSurface
from observability import record_event
from observability import compute_optimization_hint
from meta_profile import update_meta_profile_from_spans_and_self_correction
from utils_types import StatePatch


class BulletOrchestrator:
    """Coordinate bullet generation without duplicating lower-layer logic."""

    def __init__(
        self,
        reasoner: StrategyReasoner | None = None,
        executor: BulletExecutionAgent | None = None,
        state_adapter: StateAdapter | None = None,
        safety_gateway: SafetyGateway | None = None,
    ) -> None:
        self.reasoner = reasoner or StrategyReasoner()
        self.executor = executor or BulletExecutionAgent()
        self.state_adapter = state_adapter or StateAdapter()
        self.safety_gateway = safety_gateway or SafetyGateway()
        self.cost_tracker = CostTracker()

    def orchestrate(self, state: Optional[Dict[str, Any]] = None) -> OrchestrationResult:
        """Run the deterministic orchestration sequence for bullet outputs."""

        if state is not None:
            self.state_adapter.apply_patch(StatePatch(state))

        def run_plan(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            self.cost_tracker.start_span("planning")
            plan = self.reasoner.plan(current_state)
            self.cost_tracker.end_span("planning")
            plan["routing"] = {
                "complexity": "medium",
                "latency_target": 2.0,
                "cost_ceiling": 0.02,
                "risk_level": "normal",
            }
            return NodeResult(NodeStatus.SUCCESS, {"plan": plan})

        def run_execute(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            plan = context.get("plan")
            self.cost_tracker.start_span("execution")
            execution_patch = self.executor.execute(plan, current_state)
            self.cost_tracker.end_span("execution")
            return NodeResult(NodeStatus.SUCCESS, {"execution_patch": execution_patch})

        def run_patch(context: Dict[str, Any]) -> NodeResult:
            execution_patch = context.get("execution_patch")
            updated_state = self.state_adapter.apply_patch(execution_patch)
            return NodeResult(NodeStatus.SUCCESS, {"state": updated_state})

        def run_safety(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            plan = context.get("plan")
            payload = {
                "content": current_state.get("messages", []),
                "intent": plan,
                "context_tags": ["l3_orchestrator"],
            }
            safety_patch = self.safety_gateway.evaluate(payload)
            final_state = self.state_adapter.apply_patch(safety_patch)
            return NodeResult(
                NodeStatus.SUCCESS, {"safety_patch": safety_patch, "state": final_state}
            )

        dag = DAG(
            nodes={
                "plan_node": DAGNode(
                    name="plan_node",
                    run=run_plan,
                    condition=lambda ctx: bool(ctx.get("force_execute")),
                    conditional_edges={"condition_true": ["execute_node"]},
                ),
                "execute_node": DAGNode(
                    name="execute_node",
                    run=run_execute,
                    fallback_edge="plan_node",
                    retries=1,
                ),
                "patch_node": DAGNode(
                    name="patch_node",
                    run=run_patch,
                    parallel=["safety_node"],
                ),
                "safety_node": DAGNode(name="safety_node", run=run_safety),
            },
            edges={
                "plan_node": ["execute_node"],
                "execute_node": ["patch_node"],
                "patch_node": ["safety_node"],
                "safety_node": [],
            },
        )

        executor = DAGExecutor()
        initial_context = {"state": self.state_adapter.state}
        final_context = executor.run(dag, initial_context)

        final_state = final_context.get("state", {})
        surface = SelfCorrectionSurface.STRATEGY_REPLAN
        recommendation = evaluate_correction(surface, final_state, final_context)
        record_correction_event(surface.value, recommendation, final_context.get("plan", {}))

        existing_self_correction = final_state.get("self_correction", {})
        if not isinstance(existing_self_correction, dict):
            existing_self_correction = {}
        existing_self_correction.update(
            {"surface": surface.value, "recommendation": recommendation}
        )
        final_state = self.state_adapter.apply_patch(
            StatePatch({"self_correction": existing_self_correction})
        )

        spans = self.cost_tracker.snapshot()
        ct_patch = StatePatch({"telemetry": spans})
        final_state = self.state_adapter.apply_patch(ct_patch)

        optimization = compute_optimization_hint(spans.get("spans", []))
        telemetry_block = final_state.get("telemetry", {})
        if not isinstance(telemetry_block, dict):
            telemetry_block = {}
        telemetry_block["optimization"] = optimization
        final_state = self.state_adapter.apply_patch(StatePatch({"telemetry": telemetry_block}))

        plan = final_context.get("plan", {})
        record_event(
            "orchestrator_cycle",
            {
                "plan_mode": plan.get("mode") if isinstance(plan, dict) else None,
                "spans": spans,
                "optimization": optimization,
            },
        )

        predictive_cache = final_state.get("predictive_cache", {})
        if not isinstance(predictive_cache, dict):
            predictive_cache = {}
        predictive_cache["next_hint"] = optimization
        final_state = self.state_adapter.apply_patch(StatePatch({"predictive_cache": predictive_cache}))

        self_correction_block = (
            final_state.get("self_correction") if isinstance(final_state, dict) else {}
        )
        if not isinstance(self_correction_block, dict):
            self_correction_block = {}
        update_meta_profile_from_spans_and_self_correction(
            spans.get("spans", []), self_correction_block
        )

        return OrchestrationResult(
            final_context.get("plan"),
            final_context.get("execution_patch"),
            final_context.get("safety_patch"),
            final_state,
        )
"""
L3 — QA Orchestrator

Responsibilities:
    • Govern validation workflows driven by L2 QA execution agents.
    • Align verification steps with L1 reasoning intents and L5 safety directives.
    • Aggregate validation artifacts into L4 state for traceability.

This file is scaffolded for Priority 0; implementation comes later.
"""

from typing import Any, Dict, Optional

from observability import CostTracker
from l1_reasoning import StrategyReasoner
from l2_execution import QAValidationAgent
from l4_state import StateAdapter
from l5_safety import SafetyGateway
from node_result import NodeResult, NodeStatus
from self_correction import ArbitrationEngine
from self_correction import evaluate_correction
from self_correction import record_correction_event
from self_correction import SelfCorrectionSurface
from observability import record_event
from observability import compute_optimization_hint
from meta_profile import update_meta_profile_from_spans_and_self_correction
from utils_types import StatePatch


class QAOrchestrator:
    """Govern QA validation without embedding lower-layer logic."""

    def __init__(
        self,
        reasoner: StrategyReasoner | None = None,
        executor: QAValidationAgent | None = None,
        state_adapter: StateAdapter | None = None,
        safety_gateway: SafetyGateway | None = None,
    ) -> None:
        self.reasoner = reasoner or StrategyReasoner()
        self.executor = executor or QAValidationAgent()
        self.state_adapter = state_adapter or StateAdapter()
        self.safety_gateway = safety_gateway or SafetyGateway()
        self.arbitration_engine = ArbitrationEngine()
        self.cost_tracker = CostTracker()

    def orchestrate(self, state: Optional[Dict[str, Any]] = None) -> OrchestrationResult:
        """Run plan→execute→patch→safety in order."""

        if state is not None:
            self.state_adapter.apply_patch(StatePatch(state))

        def run_plan(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            self.cost_tracker.start_span("planning")
            plan = self.reasoner.plan(current_state)
            self.cost_tracker.end_span("planning")
            plan["routing"] = {
                "complexity": "medium",
                "latency_target": 2.0,
                "cost_ceiling": 0.02,
                "risk_level": "normal",
            }
            return NodeResult(NodeStatus.SUCCESS, {"plan": plan})

        def run_execute(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            plan = context.get("plan")
            self.cost_tracker.start_span("execution")
            execution_patch = self.executor.execute(plan, current_state)
            self.cost_tracker.end_span("execution")
            return NodeResult(NodeStatus.SUCCESS, {"execution_patch": execution_patch})

        def run_patch(context: Dict[str, Any]) -> NodeResult:
            execution_patch = context.get("execution_patch")
            updated_state = self.state_adapter.apply_patch(execution_patch)
            return NodeResult(NodeStatus.SUCCESS, {"state": updated_state})

        def run_safety(context: Dict[str, Any]) -> NodeResult:
            current_state = context.get("state", {})
            plan = context.get("plan")
            payload = {
                "content": current_state.get("qa_report", {}),
                "intent": plan,
                "context_tags": ["l3_orchestrator"],
            }
            safety_patch = self.safety_gateway.evaluate(payload)
            final_state = self.state_adapter.apply_patch(safety_patch)
            return NodeResult(
                NodeStatus.SUCCESS, {"safety_patch": safety_patch, "state": final_state}
            )

        dag = DAG(
            nodes={
                "plan_node": DAGNode(
                    name="plan_node",
                    run=run_plan,
                    condition=lambda ctx: bool(ctx.get("force_execute")),
                    conditional_edges={"condition_true": ["execute_node"]},
                ),
                "execute_node": DAGNode(
                    name="execute_node",
                    run=run_execute,
                    fallback_edge="plan_node",
                    retries=1,
                ),
                "patch_node": DAGNode(
                    name="patch_node",
                    run=run_patch,
                    parallel=["safety_node"],
                ),
                "safety_node": DAGNode(name="safety_node", run=run_safety),
            },
            edges={
                "plan_node": ["execute_node"],
                "execute_node": ["patch_node"],
                "patch_node": ["safety_node"],
                "safety_node": [],
            },
        )

        executor = DAGExecutor()
        initial_context = {"state": self.state_adapter.state}
        final_context = executor.run(dag, initial_context)

        updated_state = final_context.get("state", {})
        safety_patch = final_context.get("safety_patch", StatePatch({}))
        execution_patch = final_context.get("execution_patch", StatePatch({}))
        qa_report = updated_state.get("qa_report", execution_patch.get("qa_report", {}))
        if not qa_report:
            qa_report = {"findings": [{"status": "pending"}]}
            execution_patch = StatePatch({"qa_report": qa_report})
        decision = self.arbitration_engine.evaluate(updated_state, qa_report, safety_patch)

        arbitration_patch: StatePatch = StatePatch(
            {
                "self_correction": {
                    "surface": SelfCorrectionSurface.QA_RECHECK.value,
                    "decision": decision,
                }
            }
        )
        final_state = self.state_adapter.apply_patch(arbitration_patch)

        surface = SelfCorrectionSurface.QA_RECHECK
        recommendation = evaluate_correction(surface, final_state, execution_patch)
        record_correction_event(surface.value, recommendation, final_context.get("plan", {}))

        self_correction = final_state.get("self_correction", {})
        if not isinstance(self_correction, dict):
            self_correction = {}
        self_correction.update(
            {
                "surface": surface.value,
                "decision": decision,
                "recommendation": recommendation,
            }
        )
        final_state = self.state_adapter.apply_patch(StatePatch({"self_correction": self_correction}))

        spans = self.cost_tracker.snapshot()
        ct_patch = StatePatch({"telemetry": spans})
        final_state = self.state_adapter.apply_patch(ct_patch)

        optimization = compute_optimization_hint(spans.get("spans", []))
        telemetry_block = final_state.get("telemetry", {})
        if not isinstance(telemetry_block, dict):
            telemetry_block = {}
        telemetry_block["optimization"] = optimization
        final_state = self.state_adapter.apply_patch(StatePatch({"telemetry": telemetry_block}))

        plan = final_context.get("plan", {})
        record_event(
            "orchestrator_cycle",
            {
                "plan_mode": plan.get("mode") if isinstance(plan, dict) else None,
                "spans": spans,
                "optimization": optimization,
            },
        )

        predictive_cache = final_state.get("predictive_cache", {})
        if not isinstance(predictive_cache, dict):
            predictive_cache = {}
        predictive_cache["next_hint"] = optimization
        final_state = self.state_adapter.apply_patch(StatePatch({"predictive_cache": predictive_cache}))

        self_correction_block = (
            final_state.get("self_correction") if isinstance(final_state, dict) else {}
        )
        if not isinstance(self_correction_block, dict):
            self_correction_block = {}
        update_meta_profile_from_spans_and_self_correction(
            spans.get("spans", []), self_correction_block
        )

        return OrchestrationResult(
            final_context.get("plan"),
            final_context.get("execution_patch"),
            final_context.get("safety_patch"),
            final_state,
        )
