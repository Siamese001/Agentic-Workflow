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
"""L1 bullet planning stack (v10_9 compatibility shim)."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


# Minimal plan models to align with v10_7 naming used throughout the codebase.
class BulletPlan(BaseModel):
    """Lightweight bullet generation plan."""

    goal: str = "Generate resume bullets aligned to the target role."
    job_profile: Dict[str, Any] = {}
    resume_profile: Dict[str, Any] = {}
    sections: List[str] = []
    metrics: Dict[str, Any] = {}
    constraints: List[str] = []


def extract_job_profile(state: Dict[str, Any]) -> Dict[str, Any]:
    job = state.get("job") or {}
    return job.get("job_description") or job


def extract_resume_profile(state: Dict[str, Any]) -> Dict[str, Any]:
    resume = state.get("resume") or {}
    return resume.get("master_resume") or resume


def collect_sections(state: Dict[str, Any]) -> List[str]:
    resume = extract_resume_profile(state)
    experience = resume.get("experience") if isinstance(resume, dict) else []
    if isinstance(experience, list) and experience:
        return [item.get("title", f"experience_{idx + 1}") for idx, item in enumerate(experience)]
    return []


def detect_metrics(resume_profile: Dict[str, Any]) -> Dict[str, Any]:
    metrics: Dict[str, Any] = {}
    if not isinstance(resume_profile, dict):
        return metrics
    for item in resume_profile.get("experience", []) or []:
        if not isinstance(item, dict):
            continue
        for key, value in item.items():
            if isinstance(value, (int, float)):
                metrics[key] = value
    return metrics


class BulletPlanningStack:
    """Pure planning stack that prepares bullet generation intents."""

    async def run_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        job_profile = extract_job_profile(state)
        resume_profile = extract_resume_profile(state)
        sections = collect_sections(state)
        metrics = detect_metrics(resume_profile)

        plan = BulletPlan(
            job_profile=job_profile,
            resume_profile=resume_profile,
            sections=sections,
            metrics=metrics,
            constraints=["keep bullets concise", "reflect measurable impact"],
        )

        return {"bullets": {"plan": plan.model_dump()}}
"""
L2 — Bullet Execution Agent

Responsibilities:
    • Generate concise bulletized outputs from higher-level plans.
    • Respect formatting and structural constraints provided by L1 strategy reasoners.
    • Produce deterministic updates for L4 state without coordinating other agents.

Consumes PlanObject inputs and returns StatePatch outputs deterministically.
"""
from __future__ import annotations

from typing import Any, Dict, List

from injection_tooling_profiles import DEFAULT_TOOLING_PROFILE
from l2_execution import ExecutionAgent
from utils_types import PlanObject, StatePatch


class BulletExecutionAgent(ExecutionAgent):
    """Convert planning intents into bulletized state patches."""

    def execute(self, plan: PlanObject, state: Dict[str, Any]) -> StatePatch:
        items: List[str] = [str(item) for item in plan.get("deliverables", plan.get("items", []))]
        if not items:
            items = [str(plan.get("objective", "unspecified-objective"))]

        bullets = [f"- {item}" for item in items]
        message = "\n".join(bullets)

        messages = list(state.get("messages", [])) + [
            {
                "role": "assistant",
                "content": message,
                "format": "bullets",
            }
        ]

        patch: StatePatch = StatePatch(
            {
                "messages": messages,
                "last_bullets": bullets,
            }
        )
        patch["tooling_injection"] = {
            "tool_feedback_enabled": DEFAULT_TOOLING_PROFILE.tool_feedback_enabled,
            "evidence_binding_enabled": DEFAULT_TOOLING_PROFILE.evidence_binding_enabled,
            "cross_tool_reconciliation": DEFAULT_TOOLING_PROFILE.cross_tool_reconciliation,
        }
        return patch
