# FILE: v10_9_clean/l3/bullet_orchestrator.py
"""
L3 — Bullet Orchestrator (v10_9)

Bridges:
    • L1 bullet planning  → plan: PlanObject(mode="bullets")
    • L2 bullet execution → execute_bullets()

Behaviors:
    • Applies deterministic phase transitions (L3 ControlFlow)
    • Invokes L2 execution
    • Returns WorkflowState for L4 state integration
"""

from __future__ import annotations

from typing import Any, Dict

from shared.models import (
    PlanObject,
    WorkflowState,
    PhaseMetadata,
    ExecutionResult,
)
from shared.constants import WorkflowPhase
from shared.exceptions import OrchestrationError

from l3.control_flow import ControlFlow
from l2.bullet_execution import execute_bullets


class BulletOrchestrator:
    """Coordinates the bullet-generation workflow at L3."""

    def __init__(self) -> None:
        self.cf = ControlFlow()

    async def run(self, plan: PlanObject, state: Dict[str, Any]) -> WorkflowState:
        """
        Process an L1 bullet-generation plan.

        Steps:
            1. planning → executing
            2. Run L2 bullet executor
            3. executing → reviewing
            4. Pack results into WorkflowState (for L4)
        """
        try:
            # Phase: planning → executing
            phase_exec = self.cf.next_phase("planning")

            result: ExecutionResult = await execute_bullets(plan, state)

            # Phase: executing → reviewing
            phase_rev = self.cf.next_phase("executing")

            new_state = dict(state)
            new_state["bullet_result"] = result.payload

            return WorkflowState(
                workflow_id=new_state.get("workflow_id", "unknown"),
                phase=phase_rev,
                nodes={},
                state=new_state,
                phase_metadata=PhaseMetadata(
                    phase=phase_rev,
                    note="Bullet generation orchestration step complete."
                ),
            )

        except Exception as exc:
            raise OrchestrationError(f"Bullet Orchestrator failed: {exc}") from exc
