"""Local orchestrator for RAG planning and execution."""
from __future__ import annotations

from typing import Any, Dict, Optional

from rag_planning import RAGPlanningStack
from rag_execution import RAGExecutionStack


class RAGOrchestratorStack:
    """Runs planning then execution for retrieval tasks."""

    def __init__(self):
        self.planner = RAGPlanningStack()
        self.executor = RAGExecutionStack()

    async def run_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        plan_patch = await self.planner.run_async(state, workflow_id)
        interim_state = {**state, **plan_patch}
        exec_patch = await self.executor.run_async(interim_state, workflow_id)
        final_state = {**interim_state, **exec_patch}
        return final_state
