"""QA validation stack shim for v10.8."""

from __future__ import annotations

from typing import Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - import for type hints only
    from agent_orchestration_v10_7 import QAConductorAgent


class QAValidationStack:
    """Delegates QA validation to the v10.7 conductor."""

    def __init__(self, context: Any, debug_mode: bool = False) -> None:
        self.context = context
        self.debug_mode = debug_mode
        from agent_orchestration_v10_7 import QAConductorAgent as _QAConductor

        self._qa_conductor: "QAConductorAgent" = _QAConductor(context, debug_mode)

    async def run_async(self, state: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        """Forward QA validation to the existing conductor."""

        validation = await self._qa_conductor.run_async(state, workflow_id)
        final_resume = state.get("draft", {}).get("sections", {})
        qa_payload = {
            "validation_results": validation,
            "qa_passed": validation.get("qa_passed", False) if isinstance(validation, dict) else False,
        }
        artifacts_payload = {
            "final_resume": final_resume,
            "qa_report": validation,
        }
        return {"qa": qa_payload, "artifacts": {"artifacts": artifacts_payload}}
