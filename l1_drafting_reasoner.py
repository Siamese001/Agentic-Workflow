"""
L1 — Drafting Reasoner

Responsibilities:
    • Plan narrative or structured drafts aligned with task objectives.
    • Translate strategy intents into drafting briefs for L2 execution agents.
    • Incorporate retrieval or bullet inputs while deferring orchestration to L3.

Implements deterministic planning logic that emits only PlanObject instances.
"""
from __future__ import annotations

from typing import Any, Dict, List

from l1_reasoner_base import Reasoner
from utils_types import PlanObject


def _collect_sections(state: Dict[str, Any]) -> List[str]:
    """Assemble deterministic section headings for the draft."""

    if state.get("outline"):
        return [str(section) for section in state["outline"]]

    bullets = state.get("bullets") or []
    if bullets:
        return [f"Section {index + 1}: {bullet}" for index, bullet in enumerate(bullets)]

    return ["Introduction", "Body", "Conclusion"]


class DraftingReasoner(Reasoner):
    """Create drafting briefs for L2 executors without side effects."""

    def plan(self, state: Dict[str, Any]) -> PlanObject:
        objective = state.get("objective", "unspecified-objective")
        tone = state.get("tone", "neutral")
        audience = state.get("audience", "general")
        sections = _collect_sections(state)

        plan: PlanObject = PlanObject(
            {
                "layer": "l1",
                "mode": "drafting",
                "objective": str(objective),
                "tone": tone,
                "audience": audience,
                "sections": sections,
                "constraints": state.get("constraints", []),
                "handoff": {
                    "target_layer": "l2",
                    "preferred_executor": "drafting",
                    "format": "narrative",
                },
            }
        )
        plan["safety_metadata"] = {
            "objective": str(objective),
            "sensitivity": "low",
            "audience": audience,
            "tags": ["planning"],
        }
        return plan
