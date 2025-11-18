# FILE: v10_9_clean/l3/strategy_orchestrator.py
"""
L3 — Strategy Orchestrator (v10_9)

Coordinates the high-level reasoning workflow:
    • Receives an L1 Strategy plan (mode="strategy")
    • Executes decomposition / outline generation via L2
    • Applies deterministic phase transitions (ControlFlow)
    • Returns a WorkflowState for L4 integration

This replaces the orchestration behavior from:
    • strategy_stack.py (10_8)
    • strategy_ensemble_v10_7.py (10_7)
while conforming to L1–L5 separation constraints.
"""

from __future__ import annotations

from typing import Any, Dict

from shared.models import (
    PlanObject,
    WorkflowState,
    PhaseMetadata,
    ExecutionResult,
)
from shared.exceptions import OrchestrationError
from l3.control_flow import ControlFlow
from l2.strategy_execution import execute_strategy


class StrategyOrchestrator:
    """Coordinates strategy-reasoning workflows at L3."""

    def __init__(self) -> None:
        self.cf = ControlFlow()

    async def run(self, plan: PlanObject, state: Dict[str, Any]) -> WorkflowState:
        """
        Steps:
            1. PLANNING → EXECUTING
            2. Execute strategy reasoning via L2
            3. EXECUTING → REVIEWING
            4. Package result into a WorkflowState
        """
        try:
            # Step 1: planning → executing
            phase_exec = self.cf.next_phase("planning")

            # Step 2: run L2 strategy executor
            result: ExecutionResult = await execute_strategy(plan, state)

            # Step 3: executing → reviewing
            phase_rev = self.cf.next_phase("executing")

            # Step 4: form new state
            new_state = dict(state)
            new_state["strategy_result"] = result.payload

            return WorkflowState(
                workflow_id=new_state.get("workflow_id", "unknown"),
                phase=phase_rev,
                nodes={},
                state=new_state,
                phase_metadata=PhaseMetadata(
                    phase=phase_rev,
                    note="Strategy orchestration step complete."
                ),
            )

        except Exception as exc:
            raise OrchestrationError(f"Strategy Orchestrator failed: {exc}") from exc
