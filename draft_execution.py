"""Draft execution stack."""
from __future__ import annotations

from typing import Any, Dict


class DraftingExecutionStack:
    """Assembles final drafts from plans and bullets."""

    def __init__(self, context: Any, debug_mode: bool = False) -> None:
        self.context = context
        self.debug_mode = debug_mode

    async def run_async(
        self,
        state: Dict[str, Any],
        bullet_payload: Dict[str, Any],
        draft_plan_payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        sections = draft_plan_payload.get("draft", {}).get("plan", {}).get("sections", [])
        bullets = bullet_payload.get("bullets", {}).get("generated", [])
        draft_sections = {
            section: f"Section {section} with {len(bullets)} bullets"
            for section in sections
        }
        return {"draft": {"sections": draft_sections}}
