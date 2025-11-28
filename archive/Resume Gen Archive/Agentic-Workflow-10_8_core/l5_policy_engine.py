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

from l5_policy import PolicyRule, SafetyConfig, load_default_safety_config
from utils_types import StatePatch


class PolicyEngine:
    """Deterministic policy evaluation engine."""

    def __init__(self, config: SafetyConfig | None = None) -> None:
        self._config = config or load_default_safety_config()

    def evaluate(self, intent: Dict[str, str] | None = None) -> StatePatch:
        """Return a StatePatch describing policy allowances for the given intent."""

        intent = intent or {}
        action = intent.get("action", "unspecified")
        rule = next(
            (policy_rule for policy_rule in self._config.policy_rules if policy_rule.action == action),
            PolicyRule(action=action, allowed=True, reason=None),
        )
        allowed = rule.allowed

        patch: StatePatch = StatePatch(
            {
                "policy_evaluation": {
                    "action": action,
                    "allowed": allowed,
                    "denied_reason": rule.reason if not allowed else None,
                    "denied_actions": [policy_rule.action for policy_rule in self._config.policy_rules if not policy_rule.allowed],
                }
            }
        )
        return patch
