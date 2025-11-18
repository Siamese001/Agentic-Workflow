# FILE: v10_9_clean/l1/bullet_planning.py
"""
L1 — Bullet Planning (v10_9)

Pure planning layer for bullet generation.

Takes orchestration state and produces a PlanObject describing:
    • which sections to target
    • highlight order
    • metrics focus
    • style guidelines
    • validation checks

No execution, no state mutation, no external calls.
"""

from __future__ import annotations
from typing import Any, Dict, List

from models import PlanObject
from .planning_utils import (
    extract_job_profile,
    extract_resume_profile,
    collect_sections,
    describe_experience,
    detect_metrics,
)


def _highlight_order(job_profile: Dict[str, Any], experiences: List[Dict[str, Any]]) -> List[str]:
    if experiences:
        return [describe_experience(exp) for exp in experiences[:3]]

    title = job_profile.get("title") or "target role"
    return [f"Show relevant wins for {title}"]


def _style_guidelines(job_profile: Dict[str, Any], state: Dict[str, Any]) -> List[str]:
    strategy_plan = state.get("strategy", {}).get("strategy_plan") or {}
    if hasattr(strategy_plan, "model_dump"):
        strategy_plan = strategy_plan.model_dump()

    tone = strategy_plan.get("tone") or "Professional"
    guidelines = [
        f"Use a {tone.lower()} tone anchored in measurable outcomes",
        "Lead with action + metric + outcome structure",
    ]

    reqs = job_profile.get("requirements") or []
    if reqs:
        guidelines.append(
            f"Mirror JD keywords such as {', '.join(reqs[:3])}"
        )

    return guidelines


def _validation_checks(job_profile: Dict[str, Any], experiences: List[Dict[str, Any]]) -> List[str]:
    checks = [
        "Each bullet must cite a unique accomplishment",
        "Avoid repeating the same metric more than once",
        "Ensure bullets stay within one sentence",
    ]

    if job_profile.get("company"):
        checks.append(
            f"Map at least one bullet to {job_profile['company']} priorities"
        )
    if not experiences:
        checks.append("Fallback to summary insights if experience is sparse")

    return checks


def build_bullet_plan(state: Dict[str, Any]) -> PlanObject:
    job_profile = extract_job_profile(state)
    resume_profile = extract_resume_profile(state)

    experiences: List[Dict[str, Any]] = resume_profile["experiences"]
    sections = collect_sections(state)
    highlights = _highlight_order(job_profile, experiences)
    metrics_focus = detect_metrics(experiences)
    guidelines = _style_guidelines(job_profile, state)
    checks = _validation_checks(job_profile, experiences)

    steps = [
        {
            "id": "bullet_plan",
            "action": "generate_bullets",
            "target_sections": sections,
            "highlight_order": highlights,
            "metrics_focus": metrics_focus,
            "style_guidelines": guidelines,
            "validation_checks": checks,
        }
    ]

    objective = state.get("objective") or state.get("task") or "bullet-generation"

    return PlanObject(
        plan_id="l1-bullet-plan",
        description=f"Bullet generation plan for: {objective}",
        steps=steps,
        layer="l1",
        mode="bullets",
        objective=str(objective),
        constraints=[],
        dependencies=[],
        deliverables=["bullets"],
        sections=sections,
        handoff={
            "target_layer": "l2",
            "preferred_executor": "bullets",
        },
        injection_framing=state.get("injection_framing", {}),
        injection_reasoning=state.get("injection_reasoning", {}),
        safety_metadata={
            "objective": str(objective),
            "sensitivity": "low",
            "audience": state.get("audience", "general"),
            "tags": ["planning", "bullets"],
        },
    )


def plan(state: Dict[str, Any]) -> PlanObject:
    return build_bullet_plan(state)
