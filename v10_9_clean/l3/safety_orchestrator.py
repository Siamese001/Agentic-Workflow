# FILE: v10_9_clean/l3/safety_orchestrator.py
"""
L3 — Safety Orchestrator (v10_9)

Coordinates the safety-validation workflow:
    • Accepts an L1 Safety plan (mode="safety")
    • Runs L2 safety execution
    • Applies deterministic ControlFlow transitions
    • Packs the results into a WorkflowState for L4 integration

This replaces orchestration behaviors from safety_stack.py (10_7/10_8)
while respecting the L1–L5 separation.
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
from l2.safety_execution import execute_safety


class SafetyOrchestrator:
    """Coordinates safety workflows in the L3 orchestration layer."""

    def __init__(self) -> None:
        self.cf = ControlFlow()

    async def run(self, plan: PlanObject, state: Dict[str, Any]) -> WorkflowState:
        """
        Steps:
            1. PLANNING → EXECUTING
            2. Execute safety checks via L2
            3. EXECUTING → REVIEWING
            4. Insert results into a WorkflowState
        """

        try:
            # Phase 1: planning → executing
            phase_exec = self.cf.next_phase("planning")

            # Execute L2 safety
            result: ExecutionResult = await execute_safety(plan, state)

            # Phase 2: executing → reviewing
            phase_rev = self.cf.next_phase("executing")

            # Prepare new state
            new_state = dict(state)
            new_state["safety_result"] = result.payload

            return WorkflowState(
                workflow_id=new_state.get("workflow_id", "unknown"),
                phase=phase_rev,
                nodes={},
                state=new_state,
                phase_metadata=PhaseMetadata(
                    phase=phase_rev,
                    note="Safety orchestration step complete."
                ),
            )

        except Exception as exc:
            raise OrchestrationError(f"Safety Orchestrator failed: {exc}") from exc
