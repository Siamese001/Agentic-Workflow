# FILE: v10_9_clean/l1/draft_planning.py
"""
L1 — Draft Planning (v10_9)

Pure deterministic planning logic for narrative/structured draft creation.
Consumes orchestration state and emits a PlanObject describing:
    • sections to generate
    • tone, audience, style
    • content constraints from job & resume
    • optional hints for L2 drafting executors

No execution, no model calls, no state mutation.
"""

from __future__ import annotations
from typing import Any, Dict, List

from shared.models import PlanObject
from .planning_utils import (
    extract_job_profile,
    extract_resume_profile,
    collect_sections,
    detect_metrics,
)


def _resolve_tone(state: Dict[str, Any]) -> str:
    """Determine tone based on user or strategy metadata."""
    strategy_plan = state.get("strategy", {}).get("strategy_plan") or {}
    if hasattr(strategy_plan, "model_dump"):
        strategy_plan = strategy_plan.model_dump()

    tone = (
        state.get("tone")
        or strategy_plan.get("tone")
        or "Professional"
    )
    return str(tone)


def _resolve_audience(state: Dict[str, Any]) -> str:
    """Audience defaults to 'general' unless configured."""
    strategy_plan = state.get("strategy", {}).get("strategy_plan") or {}
    if hasattr(strategy_plan, "model_dump"):
        strategy_plan = strategy_plan.model_dump()

    return (
        state.get("audience")
        or strategy_plan.get("audience")
        or "general"
    )


def _pull_drafting_hints(job_profile: Dict[str, Any], resume_profile: Dict[str, Any]) -> List[str]:
    """Provide contextual hints based on job + resume signals."""
    hints: List[str] = []

    if job_profile.get("summary"):
        hints.append("Align opening paragraph to job summary keywords")

    if resume_profile.get("summary"):
        hints.append("Start with a strong professional summary derived from resume")

    if job_profile.get("requirements"):
        reqs = ", ".join(job_profile["requirements"][:3])
        hints.append(f"Integrate priority JD requirements: {reqs}")

    metrics = detect_metrics(resume_profile.get("experiences", []))
    if metrics:
        hints.append(metrics[0])

    return hints


def build_draft_plan(state: Dict[str, Any]) -> PlanObject:
    """Construct an L1 drafting PlanObject."""

    job_profile = extract_job_profile(state)
    resume_profile = extract_resume_profile(state)
    sections = collect_sections(state)

    tone = _resolve_tone(state)
    audience = _resolve_audience(state)
    hints = _pull_drafting_hints(job_profile, resume_profile)

    objective = (
        state.get("objective")
        or state.get("task")
        or "draft-generation"
    )

    steps = [
        {
            "id": "draft",
            "action": "generate_draft",
            "sections": sections,
            "tone": tone,
            "audience": audience,
            "hints": hints,
        }
    ]

    return PlanObject(
        plan_id="l1-draft-plan",
        description=f"Drafting plan for: {objective}",
        steps=steps,
        layer="l1",
        mode="drafting",
        objective=str(objective),
        tone=tone,
        audience=audience,
        sections=sections,
        handoff={
            "target_layer": "l2",
            "preferred_executor": "drafting",
        },
        injection_framing=state.get("injection_framing", {}),
        injection_reasoning=state.get("injection_reasoning", {}),
        safety_metadata={
            "objective": str(objective),
            "sensitivity": "low",
            "audience": audience,
            "tags": ["planning", "drafting"],
        },
    )


def plan(state: Dict[str, Any]) -> PlanObject:
    """L1 public entrypoint."""
    return build_draft_plan(state)
