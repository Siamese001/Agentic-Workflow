"""
L3 — QA Orchestrator

Responsibilities:
    • Govern validation workflows driven by L2 QA execution agents.
    • Align verification steps with L1 reasoning intents and L5 safety directives.
    • Aggregate validation artifacts into L4 state for traceability.

This file is scaffolded for Priority 0; implementation comes later.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from l3_orchestration import DAGExecutor
from l3_orchestration import DAG, DAGNode
from observability import CostTracker
from l1_reasoning import StrategyReasoner
from l2_execution import QAValidationAgent
from l3_orchestration import OrchestrationResult
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
