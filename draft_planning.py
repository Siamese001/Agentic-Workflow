"""Draft planning stack."""
from __future__ import annotations

from typing import Any, Dict


class DraftPlanningStack:
    """Generates drafting blueprints."""

    def __init__(self, context: Any, debug_mode: bool = False) -> None:
        self.context = context
        self.debug_mode = debug_mode

    async def run_async(self, state: Dict[str, Any]) -> Dict[str, Any]:
        sections = list(state.get("draft", {}).get("sections", {}).keys()) or ["summary"]
        return {"draft": {"plan": {"sections": sections}}}
