"""L2 bullet execution stack providing generation and critique shims."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class BulletPlan(BaseModel):
    goal: str = "Generate resume bullets aligned to the target role."
    job_profile: Dict[str, Any] = {}
    resume_profile: Dict[str, Any] = {}
    sections: List[str] = []
    metrics: Dict[str, Any] = {}
    constraints: List[str] = []


class StrategyPlan(BaseModel):
    tone: str = "Professional"
    style_guide: Dict[str, Any] = {}


class BulletExecutionStack:
    """Execution stack for bullet generation and critique."""

    def __init__(self, bullets_per_experience: int = 2):
        self.bullets_per_experience = bullets_per_experience

    def _load_plan(self, state: Dict[str, Any]) -> BulletPlan:
        plan_data = state.get("bullets", {}).get("plan") or {}
        if isinstance(plan_data, BulletPlan):
            return plan_data
        if isinstance(plan_data, dict):
            return BulletPlan(**plan_data)
        return BulletPlan()

    def _load_strategy(self, state: Dict[str, Any]) -> StrategyPlan:
        strategy = state.get("strategy", {}).get("strategy_plan") or {}
        if isinstance(strategy, StrategyPlan):
            return strategy
        if isinstance(strategy, dict):
            return StrategyPlan(**strategy)
        return StrategyPlan()

    def _experiences(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        resume = state.get("resume") or {}
        master = resume.get("master_resume") if isinstance(resume, dict) else {}
        experiences = master.get("experience") if isinstance(master, dict) else []
        return experiences if isinstance(experiences, list) else []

    async def generate_from_state_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        plan = self._load_plan(state)
        strategy = self._load_strategy(state)
        generated: List[Dict[str, Any]] = []
        experiences = self._experiences(state)

        for exp_index, exp in enumerate(experiences or []):
            title = exp.get("title") or exp.get("role") or f"Experience {exp_index + 1}"
            detail = exp.get("description") or exp.get("summary") or "Delivered impact."
            for bullet_index in range(self.bullets_per_experience):
                generated.append(
                    {
                        "id": f"exp{exp_index}_b{bullet_index}",
                        "text": f"{title}: {detail} (bullet {bullet_index + 1})",
                        "tone": strategy.tone,
                    }
                )

        instructions = {
            "constraints": plan.constraints,
            "goal": plan.goal,
            "tone": strategy.tone,
        }

        return {
            "bullets": {
                "plan": plan.model_dump(),
                "generated_bullets": generated,
                "instructions": instructions,
            }
        }

    async def critique_from_state_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        bullets = state.get("bullets", {}).get("generated_bullets") or []
        critiqued = []
        for item in bullets:
            text = item.get("text") if isinstance(item, dict) else str(item)
            critiqued.append({"original": text, "critique": "Reviewed for clarity."})

        plan = self._load_plan(state)
        patch: Dict[str, Any] = {
            "bullets": {
                "plan": plan.model_dump(),
                "generated_bullets": bullets,
                "critiqued_bullets": critiqued,
            }
        }
        return patch

    async def run_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        generation_patch = await self.generate_from_state_async(state, workflow_id)
        combined_state = {**state, **generation_patch}
        critique_patch = await self.critique_from_state_async(combined_state, workflow_id)

        merged_bullets = critique_patch.get("bullets", {})
        merged_bullets.setdefault("plan", self._load_plan(state).model_dump())

        final_patch: Dict[str, Any] = {"bullets": merged_bullets}
        return final_patch
