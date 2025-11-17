# policy_engine.py
"""
L5 — Policy Engine (v10_9)

Evaluates high-level policy rules against:
    • user objective
    • audience
    • sensitivity flags
    • safety report metadata

This module is deterministic and uses simple rule tables;
it is intentionally free of ML and external dependencies.
"""

from __future__ import annotations

from typing import Dict, Any

from .safety_contracts import SafetyReport


class PolicyEngine:
    """
    Stateless policy evaluator.

    Usage:
        engine = PolicyEngine()
        decision = engine.evaluate(policy_input, safety_report)
    """

    def evaluate(self, policy_input: Dict[str, Any], safety: SafetyReport) -> Dict[str, Any]:
        """
        Evaluate policy constraints and return a simple policy decision payload.

        policy_input (example keys):
            objective: high-level user task
            audience:   'general', 'internal', 'children', etc.
            sensitivity: 'low', 'medium', 'high'
        """

        objective = str(policy_input.get("objective", ""))
        audience = str(policy_input.get("audience", "general")).lower()
        sensitivity = str(policy_input.get("sensitivity", "low")).lower()

        blocked = False
        reasons = list(safety.warnings)

        # Example rules — can be extended:
        if sensitivity == "high" and not safety.is_safe:
            blocked = True
            reasons.append("High-sensitivity task with unmet safety constraints.")

        if "children" in audience and not safety.is_safe:
            blocked = True
            reasons.append("Unsafe content is not allowed for children audience.")

        return {
            "blocked": blocked,
            "reasons": reasons,
            "objective": objective,
            "audience": audience,
            "sensitivity": sensitivity,
        }
