"""Layer-3 orchestration for bullet + draft generation."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from agent_stacks_v10_8.state_adapter_stack import StateAdapterStack
from core_v10_7 import BaseAgent

from .bullet_execution import BulletExecutionStack
from .bullet_planning import BulletPlanningStack
from .draft_planning import DraftPlanningStack
from .drafting_execution import DraftingExecutionStack


class DraftOrchestratorStack(BaseAgent):
    """Runs the deterministic sequencing for bullets + draft assembly."""

    def __init__(self, context: Any, debug_mode: bool = False) -> None:
        super().__init__(context, debug_mode)
        self._adapter = StateAdapterStack(context, debug_mode)
        self._bullet_planning = BulletPlanningStack(context, debug_mode)
        self._bullet_execution = BulletExecutionStack(context, debug_mode)
        self._draft_planning = DraftPlanningStack(context, debug_mode)
        self._draft_execution = DraftingExecutionStack(context, debug_mode)

    async def run_async(
        self,
        state: Dict[str, Any],
        workflow_id: Optional[str] = None,
        state_snapshot: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        workflow_id = workflow_id or state.get("metadata", {}).get("workflow_id", "")
        current_state = state
        baseline = state_snapshot or state

        bullet_plan_patch = await self._bullet_planning.run_async(current_state, workflow_id)
        current_state = self._adapter.apply_patch(current_state, bullet_plan_patch)
        bullet_plan = (bullet_plan_patch.get("bullets", {}) or {}).get("plan", {})
        self._append_a2a_message(
            current_state,
            message_type="PLAN_CREATED",
            payload={
                "workflow_id": workflow_id,
                "sections": len(bullet_plan.get("target_sections", [])),
            },
        )

        bullet_execution_patch = await self._bullet_execution.run_async(current_state, workflow_id)
        current_state = self._adapter.apply_patch(current_state, bullet_execution_patch)
        bullets = current_state.get("bullets", {}).get("generated_bullets", [])
        self._append_a2a_message(
            current_state,
            message_type="BULLETS_GENERATED",
            payload={
                "workflow_id": workflow_id,
                "bullet_count": len(bullets),
            },
        )

        draft_plan_patch = await self._draft_planning.run_async(current_state, workflow_id)
        current_state = self._adapter.apply_patch(current_state, draft_plan_patch)
        draft_plan = (draft_plan_patch.get("draft", {}) or {}).get("plan", {})
        self._append_a2a_message(
            current_state,
            message_type="DRAFT_PLANNED",
            payload={
                "workflow_id": workflow_id,
                "structure": len(draft_plan.get("structure", [])),
            },
        )

        draft_execution_patch = await self._draft_execution.run_async(
            current_state,
            workflow_id,
        )
        current_state = self._adapter.apply_patch(current_state, draft_execution_patch)
        sections = current_state.get("draft", {}).get("sections", {})
        self._append_a2a_message(
            current_state,
            message_type="DRAFT_EXECUTED",
            payload={
                "workflow_id": workflow_id,
                "sections": len(sections),
                "baseline_sections": len(baseline.get("draft", {}).get("sections", {})),
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
