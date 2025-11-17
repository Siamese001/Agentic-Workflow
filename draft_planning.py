"""L1 draft planning stack."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from bullet_planning import extract_job_profile, extract_resume_profile, collect_sections, detect_metrics


class DraftPlan(BaseModel):
    goal: str = "Create a polished resume draft."
    tone: str = "Professional"
    structure: List[str] = ["Executive Summary", "Experience", "Skills"]
    key_messages: List[str] = []
    risks: List[str] = []
    review_gates: List[str] = []
    job_profile: Dict[str, Any] = {}
    resume_profile: Dict[str, Any] = {}


class DraftPlanningStack:
    """Prepare a draft plan without mutating state."""

    async def run_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        job_profile = extract_job_profile(state)
        resume_profile = extract_resume_profile(state)
        sections = collect_sections(state)
        metrics = detect_metrics(resume_profile)

        key_messages = []
        if isinstance(job_profile, dict):
            key_messages.extend([str(v) for v in job_profile.values() if isinstance(v, str)])
        if metrics:
            key_messages.extend([f"Metric: {k}={v}" for k, v in metrics.items()])

        structure = ["Executive Summary"] + [s for s in sections if s]
        if not structure:
            structure = ["Executive Summary", "Experience", "Education"]

        plan = DraftPlan(
            tone="Professional",
            structure=structure,
            key_messages=key_messages,
            risks=["hallucination", "missing job alignment"],
            review_gates=["narrative continuity", "quantified impact", "tone"],
            job_profile=job_profile,
            resume_profile=resume_profile,
        )

        return {"draft": {"plan": plan.model_dump()}}
