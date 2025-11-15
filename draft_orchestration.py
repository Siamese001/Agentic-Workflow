"""Draft orchestrator that coordinates bullet + draft stacks."""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from agent_stacks_v10_8.state_adapter_stack import StateAdapterStack
from bullet_execution import BulletExecutionStack
from bullet_planning import BulletPlanningStack
from draft_execution import DraftingExecutionStack
from draft_planning import DraftPlanningStack
from telemetry_v10_7 import log_event


class DraftOrchestratorStack:
    """L3 orchestrator that limits itself to control-flow coordination."""

    def __init__(self, context: Any, debug_mode: bool = False) -> None:
        self.context = context
        self.config = getattr(context, "config", None)
        self.debug_mode = debug_mode
        self._adapter = StateAdapterStack(context, debug_mode)
        self._bullet_planning = BulletPlanningStack(context, debug_mode)
        self._bullet_execution = BulletExecutionStack(context, debug_mode)
        self._draft_planning = DraftPlanningStack(context, debug_mode)
        self._draft_execution = DraftingExecutionStack(context, debug_mode)

    async def run_async(self, state: Dict[str, Any]) -> Dict[str, Any]:
        workflow_id = state.get("metadata", {}).get("workflow_id", "")
        current_state = deepcopy(state)
        cumulative_patch: Dict[str, Any] = {}

        bullet_plan = await self._bullet_planning.run_async(current_state)
        log_event(
            "DraftOrchestratorStack",
            "bullet_plan_created",
            {
                "workflow_id": workflow_id,
                "node": "BULLET_PLAN",
                "category": "signal",
                "target_sections": len(
                    bullet_plan.get("bullets", {}).get("plan", {}).get("target_sections", [])
                ),
            },
        )
        cumulative_patch = self._adapter.merge_patch(cumulative_patch, bullet_plan)
        current_state = self._adapter.apply_patch(current_state, bullet_plan)

        a2a_patch = self._adapter.build_a2a_message_patch(
            sender=self.__class__.__name__,
            message_type="BULLET_PLAN_READY",
            payload={"workflow_id": workflow_id},
        )
        cumulative_patch = self._adapter.merge_patch(cumulative_patch, a2a_patch)
        current_state = self._adapter.apply_patch(current_state, a2a_patch)

        bullet_exec_patch = await self._bullet_execution.run_async(current_state, bullet_plan)
        log_event(
            "DraftOrchestratorStack",
            "bullet_execution_completed",
            {
                "workflow_id": workflow_id,
                "node": "BULLET_EXECUTION",
                "category": "signal",
            },
        )
        cumulative_patch = self._adapter.merge_patch(cumulative_patch, bullet_exec_patch)
        current_state = self._adapter.apply_patch(current_state, bullet_exec_patch)

        draft_plan = await self._draft_planning.run_async(current_state)
        log_event(
            "DraftOrchestratorStack",
            "draft_plan_created",
            {
                "workflow_id": workflow_id,
                "node": "DRAFT_PLAN",
                "category": "signal",
                "sections": len(draft_plan.get("draft", {}).get("plan", {}).get("sections", [])),
            },
        )
        cumulative_patch = self._adapter.merge_patch(cumulative_patch, draft_plan)
        current_state = self._adapter.apply_patch(current_state, draft_plan)

        draft_exec_patch = await self._draft_execution.run_async(current_state, bullet_exec_patch, draft_plan)
        log_event(
            "DraftOrchestratorStack",
            "draft_execution_completed",
            {
                "workflow_id": workflow_id,
                "node": "DRAFT_EXECUTION",
                "category": "signal",
            },
        )
        cumulative_patch = self._adapter.merge_patch(cumulative_patch, draft_exec_patch)

        completion_patch = self._adapter.build_a2a_message_patch(
            sender=self.__class__.__name__,
            message_type="DRAFT_COMPLETED",
            payload={"workflow_id": workflow_id},
        )
        cumulative_patch = self._adapter.merge_patch(cumulative_patch, completion_patch)
        return cumulative_patch
