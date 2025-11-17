"""
L3 — Graph Orchestrator

Responsibilities:
    • Coordinate agentic workflows across a graph of tasks and dependencies.
    • Route intents from L1 reasoners to appropriate L2 execution agents.
    • Integrate safety decisions from L5 without embedding policy logic.

This file is scaffolded for Priority 0; implementation comes later.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from dag_executor import DAGExecutor
from dag_spec import DAG, DAGNode
from cost_tracker import CostTracker
from l1_strategy_reasoner import StrategyReasoner
from l2_rag_execution import RAGExecutionAgent
from l4_state_adapter import StateAdapter
from l5_safety_gateway import SafetyGateway
from node_result import NodeResult, NodeStatus
from routing_policy import RoutingCriteria, RoutingDecision, decide_route
from self_correction_surfaces import SelfCorrectionSurface
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

    def orchestrate(self, state: Optional[Dict[str, Any]] = None) -> OrchestrationResult:
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

        final_state = final_context.get("state", {})
        existing_self_correction = final_state.get("self_correction", {})
        if not isinstance(existing_self_correction, dict):
            existing_self_correction = {}
        if not existing_self_correction or existing_self_correction.get("surface") is None:
            sc_patch: StatePatch = StatePatch(
                {"self_correction": {"surface": SelfCorrectionSurface.STRATEGY_REPLAN.value}}
            )
            final_state = self.state_adapter.apply_patch(sc_patch)

        ct_patch = StatePatch({"telemetry": self.cost_tracker.snapshot()})
        final_state = self.state_adapter.apply_patch(ct_patch)

        cache_patch = StatePatch(
            {
                "predictive_cache": {"snapshot": {}},
                "tuning": {"suggestion": {"temperature": 0.3, "max_tokens": 500}},
            }
        )
        final_state = self.state_adapter.apply_patch(cache_patch)

        final_state["tooling_injection"] = {"cross_tool_reconciliation": True}

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
