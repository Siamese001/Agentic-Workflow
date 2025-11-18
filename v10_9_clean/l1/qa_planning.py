# FILE: v10_9_clean/l1/qa_planning.py
"""
L1 — QA Planning (v10_9)

Creates deterministic QA plan fragments describing:
    • which QA checks to run
    • severity mode
    • audience constraints
    • expected QA outputs (qa_report)

No execution, no state mutation.
"""

from __future__ import annotations
from typing import Any, Dict, List

from models import PlanObject


def _basic_checks() -> List[str]:
    return [
        "content_not_empty",
        "no_forbidden_phrases",
        "logical_consistency",
        "factual_coherence",
        "format_integrity",
    ]


def _sensitivity_checks(audience: str) -> List[str]:
    if audience.lower() == "children":
        return ["child_safe_language", "no_sensitive_topics"]
    return []


def _severity_profile(state: Dict[str, Any]) -> str:
    return (
        state.get("qa_severity")
        or state.get("qa", {}).get("severity")
        or "normal"
    )


def build_qa_plan(state: Dict[str, Any]) -> PlanObject:
    audience = state.get("audience", "general")
    severity = _severity_profile(state)

    checks = _basic_checks()
    checks.extend(_sensitivity_checks(audience))

    objective = state.get("objective") or "qa-validation"

    steps = [
        {
            "id": "qa_validate",
            "action": "execute_qa",
            "checks": checks,
            "severity": severity,
            "audience": audience,
        }
    ]

    return PlanObject(
        plan_id="l1-qa-plan",
        description=f"QA validation plan for: {objective}",
        steps=steps,
        layer="l1",
        mode="qa",
        objective=str(objective),
        constraints=[],
        dependencies=[],
        deliverables=["qa_report"],
        handoff={
            "target_layer": "l2",
            "preferred_executor": "qa",
        },
        injection_framing=state.get("injection_framing", {}),
        injection_reasoning=state.get("injection_reasoning", {}),
        safety_metadata={
            "objective": str(objective),
            "sensitivity": severity,
            "audience": audience,
            "tags": ["planning", "qa"],
        },
    )


def plan(state: Dict[str, Any]):
    return build_qa_plan(state)
