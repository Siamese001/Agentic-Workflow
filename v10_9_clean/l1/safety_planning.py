# FILE: v10_9_clean/l1/safety_planning.py
"""
L1 — Safety Planning (v10_9)

Creates deterministic safety plan fragments describing:
    • which safety checks to run
    • which redaction rules apply
    • sensitivity mode
    • audience restrictions
    • expected output (safety_report, sanitized content)

No execution, no state mutation.
"""

from __future__ import annotations
from typing import Any, Dict, List

from shared.models import PlanObject


# ---------------------------------------------------------------------------
# Safety rule selection
# ---------------------------------------------------------------------------

def _base_rules() -> List[str]:
    return [
        "pii_redaction",
        "forbidden_content_scan",
        "bias_scan",
        "toxicity_scan",
    ]


def _audience_rules(audience: str) -> List[str]:
    if audience.lower() == "children":
        return ["child_protection_rules"]
    return []


def _sensitivity_mode(state: Dict[str, Any]) -> str:
    return (
        state.get("safety_sensitivity")
        or state.get("safety", {}).get("mode")
        or "normal"
    )


# ---------------------------------------------------------------------------
# Main L1 builder
# ---------------------------------------------------------------------------

def build_safety_plan(state: Dict[str, Any]) -> PlanObject:
    audience = state.get("audience", "general")
    sensitivity = _sensitivity_mode(state)

    rules = _base_rules()
    rules.extend(_audience_rules(audience))

    objective = state.get("objective") or "safety-validation"

    steps = [
        {
            "id": "safety_validate",
            "action": "execute_safety",
            "rules": rules,
            "sensitivity": sensitivity,
            "audience": audience,
        }
    ]

    return PlanObject(
        plan_id="l1-safety-plan",
        description=f"Safety validation plan for: {objective}",
        steps=steps,
        layer="l1",
        mode="safety",
        objective=str(objective),
        constraints=[],
        dependencies=[],
        deliverables=["safety_report", "sanitized_content"],
        handoff={
            "target_layer": "l2",
            "preferred_executor": "safety",
        },
        injection_framing=state.get("injection_framing", {}),
        injection_reasoning=state.get("injection_reasoning", {}),
        safety_metadata={
            "objective": str(objective),
            "audience": audience,
            "sensitivity": sensitivity,
            "tags": ["planning", "safety"],
        },
    )


def plan(state: Dict[str, Any]):
    return build_safety_plan(state)
