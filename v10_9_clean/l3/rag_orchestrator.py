# FILE: v10_9_clean/l3/rag_orchestrator.py
"""
L3 — RAG Orchestrator (v10_9)

Bridges L1 RAG planning and L2 retrieval execution.

Responsibilities:
    • Receive the L1 RAG PlanObject
    • Select the correct L2 executor (rag_execution)
    • Run the RAG execution step
    • Package results into a WorkflowState for L4

Does NOT mutate state directly; that is L4’s responsibility.
"""

from __future__ import annotations

from typing import Any, Dict

from shared.models import PlanObject, WorkflowState, PhaseMetadata, ExecutionResult
from shared.constants import WorkflowPhase
from shared.exceptions import OrchestrationError

from l3.control_flow import ControlFlow
from l2.rag_execution import execute_rag


class RAGOrchestrator:
    """Orchestrates a single RAG execution cycle based on an L1 plan."""

    def __init__(self) -> None:
        self.cf = ControlFlow()

    async def run(self, plan: PlanObject, state: Dict[str, Any]) -> WorkflowState:
        """
        Given an L1 RAG plan:
            • Transition PLANNING → EXECUTING
            • Execute the retrieval
            • Transition EXECUTING → REVIEWING
            • Return WorkflowState with L2 results in .state
        """
        try:
            # Phase: planning → executing
            phase1 = self.cf.next_phase("planning")

            exec_result: ExecutionResult = await execute_rag(plan, state)

            # Phase: executing → reviewing
            phase2 = self.cf.next_phase("executing")

            new_state = dict(state)
            new_state["rag_result"] = exec_result.payload

            return WorkflowState(
                workflow_id=new_state.get("workflow_id", "unknown"),
                phase=phase2,
                nodes={},
                state=new_state,
                phase_metadata=PhaseMetadata(
                    phase=phase2,
                    note="RAG orchestration step complete."
                ),
            )

        except Exception as exc:
            raise OrchestrationError(f"RAG Orchestrator failed: {exc}") from exc
