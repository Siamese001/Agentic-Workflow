"""Bullet execution stack."""
from __future__ import annotations

from typing import Any, Dict, List


class BulletExecutionStack:
    """Generates bullet drafts for targeted sections."""

    def __init__(self, context: Any, debug_mode: bool = False) -> None:
        self.context = context
        self.debug_mode = debug_mode

    async def run_async(self, state: Dict[str, Any], plan_payload: Dict[str, Any]) -> Dict[str, Any]:
        sections: List[int] = plan_payload.get("bullets", {}).get("plan", {}).get("target_sections", [])
        bullets = [
            {"section": section, "text": f"Bullet for section {section}"}
            for section in sections
        ]
        return {"bullets": {"generated": bullets}}
