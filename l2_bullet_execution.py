"""
L2 — Bullet Execution Agent

Responsibilities:
    • Generate concise bulletized outputs from higher-level plans.
    • Respect formatting and structural constraints provided by L1 strategy reasoners.
    • Produce deterministic updates for L4 state without coordinating other agents.

Consumes PlanObject inputs and returns StatePatch outputs deterministically.
"""
from __future__ import annotations

from typing import Any, Dict, List

from injection_tooling_profiles import DEFAULT_TOOLING_PROFILE
from l2_tool_base import ExecutionAgent
from utils_types import PlanObject, StatePatch


class BulletExecutionAgent(ExecutionAgent):
    """Convert planning intents into bulletized state patches."""

    def execute(self, plan: PlanObject, state: Dict[str, Any]) -> StatePatch:
        items: List[str] = [str(item) for item in plan.get("deliverables", plan.get("items", []))]
        if not items:
            items = [str(plan.get("objective", "unspecified-objective"))]

        bullets = [f"- {item}" for item in items]
        message = "\n".join(bullets)

        messages = list(state.get("messages", [])) + [
            {
                "role": "assistant",
                "content": message,
                "format": "bullets",
            }
        ]

        patch: StatePatch = StatePatch(
            {
                "messages": messages,
                "last_bullets": bullets,
            }
        )
        patch["tooling_injection"] = {
            "tool_feedback_enabled": DEFAULT_TOOLING_PROFILE.tool_feedback_enabled,
            "evidence_binding_enabled": DEFAULT_TOOLING_PROFILE.evidence_binding_enabled,
            "cross_tool_reconciliation": DEFAULT_TOOLING_PROFILE.cross_tool_reconciliation,
        }
        return patch
