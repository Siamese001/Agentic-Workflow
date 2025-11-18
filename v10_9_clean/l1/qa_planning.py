# FILE: v10_9_clean/l1/qa_planning.py
"""
L1 — QA Planning (v10_9)

Creates deterministic QA plan fragments that describe:
    • what content to validate
    • which checks to run
    • expected structure of QA results
    • severity thresholds
    • whether the result should trigger replan / retry

This replaces 10_7 qa_validation_stack's planning surface,
aligned to the 10_9 L1 cognition layer.
"""

from __future__ import annotations

from typing import Any, Dict, List

from shared.models import PlanObject


# ---------------------------------------------------------------------------
# QA rule generation
# ---------------------------------------------------------------------------

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
    """Severity defaults to 'normal' unless state overrides."""
    return (
        state.get("qa_severity")
        or state.get("qa", {}).get("severity")
        or "normal"
    )


# ---------------------------------------------------------------------------
# Main L1 Plan Builder
# ---------------------------------------------------------------------------

def build_qa_plan(state: Dict[str, Any]) -> PlanObject:
    """
    Build a QA PlanObject that defines:
        • validation checks to run
        • severity level
        • expected output: qa_report = { issues[], confidence }
    """

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
            "sensitivity": "low",
            "audience": audience,
            "tags": ["planning", "qa"],
        },
    )


def plan(state: Dict[str, Any]):
    """Public L1 entrypoint."""
    return build_qa_plan(state)
