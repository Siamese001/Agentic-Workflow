"""Deterministic Level-1 planner for the drafting stack."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from core_v10_7 import BaseAgent, DraftPlan

from .planning_utils import (
    collect_sections,
    describe_experience,
    extract_job_profile,
    extract_resume_profile,
    missing_requirements,
)


class DraftPlanningStack(BaseAgent):
    """Creates a low-latency drafting plan using only state inspection."""

    def __init__(self, context: Any, debug_mode: bool = False) -> None:
        super().__init__(context, debug_mode)

    async def run_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        plan = self._build_plan(state)
        return {"draft": {"plan": plan.model_dump()}}

    def _build_plan(self, state: Dict[str, Any]) -> DraftPlan:
        job_profile = extract_job_profile(state)
        resume_profile = extract_resume_profile(state)
        experiences = resume_profile["experiences"]
        structure = self._structure(state, job_profile)
        tone = self._tone(state)
        key_messages = self._key_messages(job_profile, experiences, resume_profile)
        review_gates = self._review_gates(job_profile)
        risks = self._risks(job_profile, experiences)
        return DraftPlan(
            structure=structure,
            tone=tone,
            key_messages=key_messages,
            review_gates=review_gates,
            risks=risks,
        )

    def _structure(
        self, state: Dict[str, Any], job_profile: Dict[str, Any]
    ) -> List[str]:
        sections = collect_sections(state)
        structure = ["Executive Summary"]
        if job_profile["team"]:
            structure.append(f"Team Narrative – {job_profile['team']}")
        structure.extend(section.title() for section in sections if section)
        return structure

    def _tone(self, state: Dict[str, Any]) -> str:
        strategy_plan = state.get("strategy", {}).get("strategy_plan") or {}
        if hasattr(strategy_plan, "model_dump"):
            strategy_plan = strategy_plan.model_dump()
        return strategy_plan.get("tone") or "Professional"

    def _key_messages(
        self,
        job_profile: Dict[str, Any],
        experiences: List[Dict[str, Any]],
        resume_profile: Dict[str, Any],
    ) -> List[str]:
        messages: List[str] = []
        if job_profile["title"]:
            messages.append(f"Position candidate as the obvious {job_profile['title']}")
        if experiences:
            messages.append(
                f"Highlight {describe_experience(experiences[0])} as the anchor story"
            )
        if resume_profile["summary"]:
            messages.append("Carry forward unique resume summary language")
        if job_profile["requirements"]:
            messages.append(
                f"Explicitly cover JD focus areas: {', '.join(job_profile['requirements'][:3])}"
            )
        return messages

    def _review_gates(self, job_profile: Dict[str, Any]) -> List[str]:
        gates = [
            "Narrative continuity review",
            "Quantified impact audit",
            "QA + tone alignment check",
        ]
        if job_profile["location"]:
            gates.append("Localization + market nuance review")
        return gates

    def _risks(
        self,
        job_profile: Dict[str, Any],
        experiences: List[Dict[str, Any]],
    ) -> List[str]:
        risks = ["Guard against hallucinating responsibilities not in resume"]
        missing = missing_requirements(job_profile["requirements"], experiences)
        if missing:
            risks.append(
                f"JD gaps detected: {', '.join(missing[:3])}. Address proactively."
            )
        return risks
