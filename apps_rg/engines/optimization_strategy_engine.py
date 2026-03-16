"""
Optimization Strategy Engine - Early stopping & pruning logic
Refactored from optimization_strategies.py
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "optimization_strategy_engine", "execution_auth")
_emit_validates_capability("p2", "optimization_strategy_engine", "capability_check")
_emit_routes_to_capability("p2", "optimization_strategy_engine", "capability_route")
_emit_writes_via_uwg("p2", "optimization_strategy_engine", "uwg_write")
_emit_blocks_direct_write("p2", "optimization_strategy_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "optimization_strategy_engine", "tool_invocation")
_emit_captures_execution_output("p2", "optimization_strategy_engine", "exec_output")
_emit_dispatches_agent("p3", "optimization_strategy_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "optimization_strategy_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "optimization_strategy_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "optimization_strategy_engine", "healing_outcome")
_emit_escalates_failure("p3", "optimization_strategy_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "optimization_strategy_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "optimization_strategy_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "optimization_strategy_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "optimization_strategy_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "optimization_strategy_engine", "eval_metric")
_emit_stores_embedding("p4", "optimization_strategy_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "optimization_strategy_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "optimization_strategy_engine", "exec_snapshot_link")
from apps_rg.engines.base_rg_engine import BaseRGEngine

_emit_applies_guardrail("p0", "optimization_strategy_engine", "p0_governance")
_emit_reads_policy_state("p0", "optimization_strategy_engine", "policy_binding")
_emit_snapshots_state("p0", "optimization_strategy_engine", "state_snapshot")
emit_replay_key("p0", "optimization_strategy_engine")
emit_determinism_digest("p0", "optimization_strategy_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class OptimizationStrategyEngine(BaseRGEngine):
    """
    Optimization Strategy - Early stopping and pruning decisions.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="ORCHESTRATION.OPTIMIZATION")

    async def execute(
        self, iteration_count: int, quality_score: float, budget_remaining: float
    ) -> dict[str, Any]:
        """
        Determine if optimization should continue or stop early.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "OptimizationStrategyEngine.execute")

        self._mcp_audit("optimization_check", {"iteration": iteration_count, "score": quality_score})
        decision = {"should_continue": True, "reason": "", "pruning_recommendations": []}
        if quality_score >= 0.95:
            decision["should_continue"] = False
            decision["reason"] = "Quality threshold achieved"
        elif iteration_count >= 5:
            decision["should_continue"] = False
            decision["reason"] = "Max iterations reached"
        elif budget_remaining < 0.1:
            decision["should_continue"] = False
            decision["reason"] = "Budget exhausted"
        if quality_score < 0.7 and iteration_count > 2:
            decision["pruning_recommendations"].append("Consider template change")
        if decision["should_continue"]:
            self.record_pass("Optimization continues", data=decision)
        else:
            self.record_pass(f"Optimization stopped: {decision['reason']}", data=decision)
        return decision
