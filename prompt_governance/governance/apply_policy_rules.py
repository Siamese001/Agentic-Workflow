"""
Apply policy rules for prompt governance.

This module provides the core policy rule application logic for validating
and enforcing prompt governance policies.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class PolicyResult:
    """Result from applying a policy rule."""

    is_compliant: bool
    policy_id: str
    message: str
    violations: List[str]


@dataclass
class PolicyRule:
    """Definition of a policy rule."""

    policy_id: str
    name: str
    description: str
    enforcement_level: str


class PromptPolicy:
    """Policy for validating prompts against governance policies."""

    def __init__(self) -> None:
        """Initialize the prompt policy."""
        self._policies: Dict[str, PolicyRule] = {}

    def register_policy(self, policy: PolicyRule) -> None:
        """Register a policy rule."""
        self._policies[policy.policy_id] = policy

    def validate(self, prompt: str) -> PolicyResult:
        """Validate a prompt against all registered policies."""
        violations: List[str] = []

        for policy_id, policy in self._policies.items():
            if not self._check_policy(prompt, policy):
                violations.append(f"{policy_id}: {policy.name}")

        return PolicyResult(
            is_compliant=len(violations) == 0,
            policy_id="ALL",
            message="Policy validation completed",
            violations=violations,
        )

    def _check_policy(self, prompt: str, policy: PolicyRule) -> bool:
        """Check a single policy against the prompt."""
        return True  # Default pass - override in subclasses

    def get_policy(self, policy_id: str) -> Optional[PolicyRule]:
        """Get a policy by ID."""
        return self._policies.get(policy_id)

    def list_policies(self) -> List[str]:
        """List all registered policy IDs."""
        return list(self._policies.keys())


def create_prompt_policy() -> PromptPolicy:
    """Factory function to create a prompt policy."""
    return PromptPolicy()


def apply_policy_rules(prompt: str, policies: List[PolicyRule]) -> PolicyResult:
    """Apply a list of policy rules to a prompt."""
    policy = PromptPolicy()
    for p in policies:
        policy.register_policy(p)
    return policy.validate(prompt)
