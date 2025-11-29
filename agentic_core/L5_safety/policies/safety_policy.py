"""
Safety Policy for L5 Safety Layer

Defines safety policies and enforcement rules.
"""

from typing import Dict, Any, List

class SafetyPolicy:
    """Base safety policy implementation."""

    def __init__(self, name: str, rules: List[str]):
        self.name = name
        self.rules = rules
        self.enabled = True

    def evaluate(self, content: str) -> Dict[str, Any]:
        """Evaluate content against safety policy."""
        violations = []

        for rule in self.rules:
            if rule.lower() in content.lower():
                violations.append(rule)

        return {
            "policy": self.name,
            "violations": violations,
            "is_safe": len(violations) == 0,
            "enabled": self.enabled
        }

    def enable(self):
        """Enable the safety policy."""
        self.enabled = True

    def disable(self):
        """Disable the safety policy."""
        self.enabled = False
