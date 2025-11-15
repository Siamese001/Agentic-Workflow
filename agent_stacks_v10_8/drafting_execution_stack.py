"""Drafting stack shim for the v10.8 layer boundary."""

from __future__ import annotations

from typing import Any, Dict, Optional

from stacks_v10_7.drafting import DraftingGuildCoordinator


class DraftingExecutionStack:
    """Delegates drafting orchestration to the v10.7 guild coordinator."""

    def __init__(self, context: Any, debug_mode: bool = False) -> None:
        self.context = context
        self.debug_mode = debug_mode
        self._guild_coordinator = DraftingGuildCoordinator(context, debug_mode)

    async def run_async(
        self,
        task_context: Dict[str, Any],
        workflow_id: str,
        state: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Forward drafting execution to the existing coordinator."""

        result = await self._guild_coordinator.run_async(task_context, workflow_id, state)
        final_sections = result.get("final_output", {}) if isinstance(result, dict) else {}
        artifacts_payload = {
            "drafting": {
                "final_output": final_sections,
                "guild_metadata": result.get("guild_metadata", {}) if isinstance(result, dict) else {},
                "overall_status": result.get("overall_status") if isinstance(result, dict) else None,
                "phases_executed": result.get("phases_executed") if isinstance(result, dict) else None,
            }
        }

        return {
            "draft": {"sections": final_sections},
            "artifacts": {"artifacts": artifacts_payload},
        }
