"""Layer-3 orchestration for the v10.8 RAG workflow."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from agent_stacks_v10_8.state_adapter_stack import StateAdapterStack
from core_v10_7 import BaseAgent

from .rag_execution import RAGExecutionStack
from .rag_planning import RAGPlanningStack


class RAGOrchestratorStack(BaseAgent):
    """Coordinates RAG planning and execution without adding new heuristics."""

    def __init__(self, context: Any, debug_mode: bool = False) -> None:
        super().__init__(context, debug_mode)
        self._adapter = StateAdapterStack(context, debug_mode)
        self._planning = RAGPlanningStack(context, debug_mode)
        self._execution = RAGExecutionStack(context, debug_mode)

    async def run_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        workflow_id = workflow_id or state.get("metadata", {}).get("workflow_id", "")
        current_state = state

        plan_patch = await self._planning.run_async(current_state, workflow_id)
        current_state = self._adapter.apply_patch(current_state, plan_patch)
        self._append_a2a_message(
            current_state,
            message_type="RAG_PLAN_CREATED",
            payload={
                "workflow_id": workflow_id,
                "goal": (plan_patch.get("rag", {}) or {}).get("plan", {}).get("goal", ""),
            },
        )

        execution_patch = await self._execution.run_async(current_state, workflow_id)
        current_state = self._adapter.apply_patch(current_state, execution_patch)
        bullets = current_state.get("resume", {}).get("experience_bullets", [])
        self._append_a2a_message(
            current_state,
            message_type="RAG_EXECUTED",
            payload={
                "workflow_id": workflow_id,
                "bullet_count": len(bullets),
            },
        )

        return current_state

    def _append_a2a_message(
        self, state: Dict[str, Any], *, message_type: str, payload: Dict[str, Any]
    ) -> None:
        channel = state.setdefault("a2a", {})
        messages = channel.setdefault("messages", [])
        messages.append(
            {
                "sender": self.__class__.__name__,
                "recipient": "ALL",
                "message_type": message_type,
                "payload": payload,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
