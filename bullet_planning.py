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
