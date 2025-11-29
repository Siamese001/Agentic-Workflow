"""
Policy Engine for L5 Safety Layer

Manages and executes safety policies.
"""

from typing import Dict, Any
from .safety_policy import SafetyPolicy

class PolicyEngine:
    """Engine for managing and executing safety policies."""

    def __init__(self):
        self.policies: Dict[str, SafetyPolicy] = {}
        self.default_rules = ["password", "secret", "token"]

    def add_policy(self, policy: SafetyPolicy):
        """Add a safety policy to the engine."""
        self.policies[policy.name] = policy

    def remove_policy(self, policy_name: str):
        """Remove a safety policy from the engine."""
        if policy_name in self.policies:
            del self.policies[policy_name]

    def evaluate_all(self, content: str) -> Dict[str, Any]:
        """Evaluate content against all policies."""
        results = {}
        overall_safe = True
        total_violations = []

        for policy_name, policy in self.policies.items():
            if policy.enabled:
                result = policy.evaluate(content)
                results[policy_name] = result
                if not result["is_safe"]:
                    overall_safe = False
                    total_violations.extend(result["violations"])

        return {
            "overall_safe": overall_safe,
            "total_violations": total_violations,
            "policy_results": results,
            "policies_evaluated": len([p for p in self.policies.values() if p.enabled])
        }

    def create_default_policy(self, name: str = "default") -> SafetyPolicy:
        """Create a default safety policy."""
        policy = SafetyPolicy(name, self.default_rules.copy())
        self.add_policy(policy)
        return policy
