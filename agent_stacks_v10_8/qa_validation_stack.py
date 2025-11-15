"""QA validation stack shim for v10.8."""

from __future__ import annotations

from typing import Any, Dict

from agent_orchestration_v10_7 import QAConductorAgent


class QAValidationStack:
    """Delegates QA validation to the v10.7 conductor."""

    def __init__(self, context: Any, debug_mode: bool = False) -> None:
        self.context = context
        self.debug_mode = debug_mode
        self._qa_conductor = QAConductorAgent(context, debug_mode)

    async def run_async(self, state: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        """Forward QA validation to the existing conductor."""

        return await self._qa_conductor.run_async(state, workflow_id)
