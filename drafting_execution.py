"""L2 drafting execution stack."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from draft_planning import DraftPlan
from bullet_execution import BulletPlan, StrategyPlan


class DraftingExecutionStack:
    """Generate draft sections from bullets and plans."""

    def _load_plan(self, state: Dict[str, Any]) -> DraftPlan:
        plan_data = state.get("draft", {}).get("plan") or {}
        if isinstance(plan_data, DraftPlan):
            return plan_data
        if isinstance(plan_data, dict):
            return DraftPlan(**plan_data)
        return DraftPlan()

    def _load_strategy(self, state: Dict[str, Any]) -> StrategyPlan:
        strategy = state.get("strategy", {}).get("strategy_plan") or {}
        if isinstance(strategy, StrategyPlan):
            return strategy
        if isinstance(strategy, dict):
            return StrategyPlan(**strategy)
        return StrategyPlan()

    def _load_bullets(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        return state.get("bullets", {}).get("generated_bullets") or []

    async def run_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        plan = self._load_plan(state)
        strategy = self._load_strategy(state)
        bullets = self._load_bullets(state)

        sections: Dict[str, Dict[str, Any]] = {}
        structure = plan.structure or ["Executive Summary", "Experience"]

        summary_points = [b.get("text", str(b)) for b in bullets[:3]]
        sections["executive_summary"] = {
            "title": "Executive Summary",
            "content": " \n".join(summary_points) if summary_points else "Summary unavailable.",
            "tone": plan.tone or strategy.tone,
        }

        experience_content = [b.get("text", str(b)) for b in bullets]
        sections["experience"] = {
            "title": "Experience",
            "content": "\n".join(experience_content) if experience_content else "",
            "tone": plan.tone or strategy.tone,
        }

        for section in structure:
            key = section.lower().replace(" ", "_")
            sections.setdefault(key, {"title": section, "content": "", "tone": plan.tone})

        artifacts = {
            "artifacts": {
                "draft": {
                    "structure": {"sections": structure},
                    "narrative": {"summary": sections.get("executive_summary", {})},
                    "compliance": {"checks": ["basic structure applied"]},
                }
            }
        }

        return {
            "draft": {
                "plan": plan.model_dump(),
                "sections": sections,
                "tone": plan.tone,
                "structure": structure,
            },
            "artifacts": artifacts,
        }
