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
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
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
