"""
Apply guard rules for prompt governance.

This module provides the core guard rule application logic for validating
and enforcing prompt governance policies.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class GuardResult:
    """Result from applying a guard rule."""

    is_valid: bool
    rule_id: str
    message: str
    violations: List[str]


@dataclass
class GuardRule:
    """Definition of a guard rule."""

    rule_id: str
    name: str
    description: str
    severity: str


class PromptGuard:
    """Guard for validating prompts against governance rules."""

    def __init__(self) -> None:
        """Initialize the prompt guard."""
        self._rules: Dict[str, GuardRule] = {}

    def register_rule(self, rule: GuardRule) -> None:
        """Register a guard rule."""
        self._rules[rule.rule_id] = rule

    def check(self, prompt: str) -> GuardResult:
        """Check a prompt against all registered rules."""
        violations: List[str] = []

        for rule_id, rule in self._rules.items():
            if not self._validate_rule(prompt, rule):
                violations.append(f"{rule_id}: {rule.name}")

        return GuardResult(
            is_valid=len(violations) == 0,
            rule_id="ALL",
            message="Guard check completed",
            violations=violations,
        )

    def _validate_rule(self, prompt: str, rule: GuardRule) -> bool:
        """Validate a single rule against the prompt."""
        return True  # Default pass - override in subclasses

    def get_rule(self, rule_id: str) -> Optional[GuardRule]:
        """Get a rule by ID."""
        return self._rules.get(rule_id)

    def list_rules(self) -> List[str]:
        """List all registered rule IDs."""
        return list(self._rules.keys())


def create_prompt_guard() -> PromptGuard:
    """Factory function to create a prompt guard."""
    return PromptGuard()


def apply_guard_rules(prompt: str, rules: List[GuardRule]) -> GuardResult:
    """Apply a list of guard rules to a prompt."""
    guard = PromptGuard()
    for rule in rules:
        guard.register_rule(rule)
    return guard.check(prompt)
