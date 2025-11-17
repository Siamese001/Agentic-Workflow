"""Human-in-the-loop stack placeholder."""
from __future__ import annotations

from typing import Any, Dict, Optional


class HILStackV10_8:
    """Provides minimal HIL behaviors for orchestration compatibility."""

    async def detect_ambiguity_async(self, strategy_plan: Dict[str, Any], workflow_id: Optional[str] = None) -> Dict[str, Any]:
        return {"hil": {"ambiguity": strategy_plan}}

    async def summarize_feedback_async(self, human_feedback: Any, workflow_id: Optional[str] = None) -> Dict[str, Any]:
        return {"hil": {"summary": human_feedback}}

    async def route_feedback_async(self, feedback: Any, workflow_id: Optional[str] = None, state_snapshot: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"hil": {"route": "drafting", "feedback": feedback}}

    async def route_from_state_async(self, state: Dict[str, Any], workflow_id: Optional[str] = None) -> Dict[str, Any]:
        feedback = state.get("feedback")
        return await self.route_feedback_async(feedback, workflow_id, state)

    async def reconcile_feedback_async(
        self,
        draft_sections: Dict[str, Any],
        specialist_feedback: Any,
        persona_consensus: Any,
        workflow_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {"hil": {"reconciliation": {"sections": draft_sections, "feedback": specialist_feedback, "consensus": persona_consensus}}}

    async def reconcile_from_state_async(self, state: Dict[str, Any], workflow_id: Optional[str] = None) -> Dict[str, Any]:
        draft = state.get("draft", {}).get("sections", {}) if isinstance(state.get("draft"), dict) else {}
        feedback = state.get("feedback")
        return await self.reconcile_feedback_async(draft, feedback, None, workflow_id)

    async def inject_edit_from_state_async(self, state: Dict[str, Any], workflow_id: Optional[str] = None) -> Dict[str, Any]:
        draft = state.get("draft", {}).get("sections", {}) if isinstance(state.get("draft"), dict) else {}
        summary = draft.get("executive_summary", {}) if isinstance(draft, dict) else {}
        summary_text = summary.get("content", "") if isinstance(summary, dict) else ""
        summary_patch = {"draft": {"sections": {"summary": {"content": summary_text}}}}
        return summary_patch
