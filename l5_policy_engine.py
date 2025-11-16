"""
L5 — Policy Engine

Responsibilities:
    • Enforce organizational policies and guardrails on agent activities.
    • Translate policy decisions into actionable constraints for orchestration and execution layers.
    • Provide auditable policy evaluations for compliance and safety reviews.

Produces StatePatch outputs only.
"""
from __future__ import annotations

from typing import Dict, List

from utils_types import StatePatch


class PolicyEngine:
    """Deterministic policy evaluation engine."""

    DEFAULT_DENIED_ACTIONS: List[str] = ["exfiltrate_data", "execute_code", "publish_unreviewed"]

    def __init__(self, denied_actions: List[str] | None = None) -> None:
        self.denied_actions = sorted(denied_actions or list(self.DEFAULT_DENIED_ACTIONS))

    def evaluate(self, intent: Dict[str, str] | None = None) -> StatePatch:
        """Return a StatePatch describing policy allowances for the given intent."""

        intent = intent or {}
        action = intent.get("action", "unspecified")
        allowed = action not in self.denied_actions

        patch: StatePatch = StatePatch(
            {
                "policy_evaluation": {
                    "action": action,
                    "allowed": allowed,
                    "denied_reason": None if allowed else "action blocked by policy",
                    "denied_actions": self.denied_actions,
                }
            }
        )
        return patch
