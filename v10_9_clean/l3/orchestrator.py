# orchestrator.py
"""
L3 — Orchestrator (v10_9)

Coordinates workflow execution:
    • Receives PlanObject from L1
    • Delegates execution to L2 ExecutionEngine
    • Manages phase transitions via ControlFlow
    • Updates state via L4 (indirectly through L3 return values)
"""

from __future__ import annotations

from typing import Dict, Any

from ..shared.models import PlanObject, WorkflowState, PhaseMetadata
from ..shared.exceptions import OrchestrationError
from .control_flow import ControlFlow
from .routing import ExecutionEngineRouter


class Orchestrator:
    """Primary coordinator for plan → execution → review cycles."""

    def __init__(self, engine_router: ExecutionEngineRouter) -> None:
        self.engine_router = engine_router
        self.cf = ControlFlow()

    async def run(self, plan: PlanObject, state: Dict[str, Any]) -> WorkflowState:
        """
        Execute a single L1 plan using the appropriate L2 ExecutionEngine.
        Does NOT mutate state here; state updates are returned.
        """

        # PHASE: PLANNING → EXECUTING
        phase = self.cf.next_phase("planning")

        engine = self.engine_router.resolve(plan)
        if engine is None:
            raise OrchestrationError(f"No execution engine available for mode={plan.mode!r}")

        # Execute L2 workflow
        result = await engine.run(plan, state)

        # PHASE: EXECUTING → REVIEWING → COMPLETE
        next_phase = self.cf.next_phase("executing")

        workflow_state = WorkflowState(
            workflow_id=state.get("workflow_id", "unknown"),
            phase=next_phase,
            nodes={},      # L2-specific nodes not tracked here
            state=state,   # raw state to be consumed by L4
            phase_metadata=PhaseMetadata(
                phase=next_phase,
                note="Orchestration step complete."
            ),
        )

        return workflow_state
