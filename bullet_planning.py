"""Bullet planning helpers."""
from __future__ import annotations

from typing import Any, Dict, List


class BulletPlanningStack:
    """Determines which sections require bullet updates."""

    def __init__(self, context: Any, debug_mode: bool = False) -> None:
        self.context = context
        self.debug_mode = debug_mode

    async def run_async(self, state: Dict[str, Any]) -> Dict[str, Any]:
        experiences: List[Dict[str, Any]] = state.get("resume", {}).get("experience", [])
        targets = [exp.get("id", idx) for idx, exp in enumerate(experiences)]
        return {"bullets": {"plan": {"target_sections": targets}}}
