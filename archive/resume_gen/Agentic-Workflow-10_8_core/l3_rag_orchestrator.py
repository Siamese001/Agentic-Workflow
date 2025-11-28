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
from runtime.observability.utils import CostTracker, record_event, compute_optimization_hint
from l1_reasoning import RAGReasoner
from l2_execution import RAGExecutionAgent
from l3_orchestration import OrchestrationResult
from l4_state import StateAdapter
from l5_safety import SafetyGateway
from node_result import NodeResult, NodeStatus
from self_correction import evaluate_correction
from self_correction import record_correction_event
from self_correction import SelfCorrectionSurface
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
