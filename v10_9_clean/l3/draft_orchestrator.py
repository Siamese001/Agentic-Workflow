# FILE: v10_9_clean/l3/draft_orchestrator.py
"""
L3 — Draft Orchestrator (v10_9)

Bridges:
    • L1 draft planning  → PlanObject(mode="drafting")
    • L2 drafting execution → execute_drafting()

Responsibilities:
    • Apply deterministic phase transitions (ControlFlow)
    • Execute the correct L2 drafting executor
    • Wrap the results into a WorkflowState (for L4 integration)

No planning, no model calls, no state mutation here.
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
from l2.drafting_execution import execute_drafting


class DraftOrchestrator:
    """Coordinates narrative/structured drafting workflows at L3."""

    def __init__(self) -> None:
        self.cf = ControlFlow()

    async def run(self, plan: PlanObject, state: Dict[str, Any]) -> WorkflowState:
        """
        Steps:
            1. PLANNING → EXECUTING
            2. Run L2 drafting executor
            3. EXECUTING → REVIEWING
            4. Return new WorkflowState with draft results
        """
        try:
            # Step 1: planning → executing
            phase_exec = self.cf.next_phase("planning")

            # Step 2: execute draft generation
            result: ExecutionResult = await execute_drafting(plan, state)

            # Step 3: executing → reviewing
            phase_rev = self.cf.next_phase("executing")

            # Step 4: write into state wrapper (L4 will integrate)
            new_state = dict(state)
            new_state["draft_result"] = result.payload

            return WorkflowState(
                workflow_id=new_state.get("workflow_id", "unknown"),
                phase=phase_rev,
                nodes={},
                state=new_state,
                phase_metadata=PhaseMetadata(
                    phase=phase_rev,
                    note="Draft orchestration step complete."
                ),
            )

        except Exception as exc:
            raise OrchestrationError(f"Draft Orchestrator failed: {exc}") from exc
