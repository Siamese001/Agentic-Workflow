# FILE: v10_9_clean/l3/qa_orchestrator.py
"""
L3 — QA Orchestrator (v10_9)

Coordinates the QA validation workflow:
    • Receives an L1 QA plan (PlanObject with mode="qa")
    • Runs L2 QA execution (execute_qa)
    • Performs phase transitions via ControlFlow
    • Packs the result into WorkflowState for L4 integration

No model calls, no planning, no state mutation.
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
from l2.qa_execution import execute_qa


class QAOrchestrator:
    """Coordinates the QA validation workflow at L3."""

    def __init__(self) -> None:
        self.cf = ControlFlow()

    async def run(self, plan: PlanObject, state: Dict[str, Any]) -> WorkflowState:
        """
        Steps:
            1. PLANNING → EXECUTING
            2. Execute QA checks via L2
            3. EXECUTING → REVIEWING
            4. Return WorkflowState containing QA result
        """
        try:
            # Step 1: planning → executing
            phase_exec = self.cf.next_phase("planning")

            # Step 2: L2 execution
            result: ExecutionResult = await execute_qa(plan, state)

            # Step 3: executing → reviewing
            phase_rev = self.cf.next_phase("executing")

            # Step 4: package new state
            new_state = dict(state)
            new_state["qa_result"] = result.payload

            return WorkflowState(
                workflow_id=new_state.get("workflow_id", "unknown"),
                phase=phase_rev,
                nodes={},
                state=new_state,
                phase_metadata=PhaseMetadata(
                    phase=phase_rev,
                    note="QA orchestration step complete."
                ),
            )

        except Exception as exc:
            raise OrchestrationError(f"QA Orchestrator failed: {exc}") from exc
