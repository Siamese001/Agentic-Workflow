"""Deterministic Level-1 plan for bullet generation."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from core_v10_7 import BaseAgent, BulletPlan

from .planning_utils import (
    collect_sections,
    describe_experience,
    detect_metrics,
    extract_job_profile,
    extract_resume_profile,
)


class BulletPlanningStack(BaseAgent):
    """Outlines which bullets to generate before invoking execution stacks."""

    def __init__(self, context: Any, debug_mode: bool = False) -> None:
        super().__init__(context, debug_mode)

    async def run_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        plan = self._build_plan(state)
        return {"bullets": {"plan": plan.model_dump()}}

    def _build_plan(self, state: Dict[str, Any]) -> BulletPlan:
        job_profile = extract_job_profile(state)
        resume_profile = extract_resume_profile(state)
        experiences = resume_profile["experiences"]
        sections = collect_sections(state)
        highlight_order = self._highlight_order(job_profile, experiences)
        metrics_focus = detect_metrics(experiences)
        style_guidelines = self._style_guidelines(job_profile, state)
        validation_checks = self._validation_checks(job_profile, experiences)
        return BulletPlan(
            target_sections=sections,
            highlight_order=highlight_order,
            metrics_focus=metrics_focus,
            style_guidelines=style_guidelines,
            validation_checks=validation_checks,
        )

    def _highlight_order(
        self, job_profile: Dict[str, Any], experiences: List[Dict[str, Any]]
    ) -> List[str]:
        if experiences:
            ordered = [describe_experience(exp) for exp in experiences[:3]]
            return ordered
        title = job_profile["title"] or "Target role"
        return [f"Show relevant wins for {title}"]

    def _style_guidelines(
        self, job_profile: Dict[str, Any], state: Dict[str, Any]
    ) -> List[str]:
        strategy_plan = state.get("strategy", {}).get("strategy_plan") or {}
        if hasattr(strategy_plan, "model_dump"):
            strategy_plan = strategy_plan.model_dump()
        tone = strategy_plan.get("tone") or "Professional"
        guidelines = [
            f"Use a {tone.lower()} tone anchored in measurable outcomes",
            "Lead with action + metric + outcome structure",
        ]
        if job_profile["requirements"]:
            guidelines.append(
                f"Mirror JD keywords such as {', '.join(job_profile['requirements'][:3])}"
            )
        return guidelines

    def _validation_checks(
        self, job_profile: Dict[str, Any], experiences: List[Dict[str, Any]]
    ) -> List[str]:
        checks = [
            "Each bullet must cite a unique accomplishment",
            "Avoid repeating the same metric more than once",
            "Ensure bullets stay within 1 sentence",
        ]
        if job_profile["company"]:
            checks.append(
                f"Map at least one bullet to {job_profile['company']} priorities"
            )
        if not experiences:
            checks.append("Fallback to summary insights if experience is sparse")
        return checks
