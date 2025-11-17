"""Local orchestrator for bullet and draft generation."""
from __future__ import annotations

from typing import Any, Dict, Optional

from bullet_planning import BulletPlanningStack
from bullet_execution import BulletExecutionStack
from draft_planning import DraftPlanningStack
from drafting_execution import DraftingExecutionStack


class DraftOrchestratorStack:
    """Coordinates bullet planning/execution and drafting."""

    def __init__(self):
        self.bullet_planner = BulletPlanningStack()
        self.bullet_executor = BulletExecutionStack()
        self.draft_planner = DraftPlanningStack()
        self.drafting_executor = DraftingExecutionStack()

    async def run_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        bullet_plan_patch = await self.bullet_planner.run_async(state, workflow_id)
        bullet_plan_state = {**state, **bullet_plan_patch}
        bullet_exec_patch = await self.bullet_executor.run_async(bullet_plan_state, workflow_id)
        bullet_state = {**bullet_plan_state, **bullet_exec_patch}

        draft_plan_patch = await self.draft_planner.run_async(bullet_state, workflow_id)
        draft_plan_state = {**bullet_state, **draft_plan_patch}
        draft_exec_patch = await self.drafting_executor.run_async(draft_plan_state, workflow_id)

        final_state = {**draft_plan_state, **draft_exec_patch}
        return final_state
