from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

# Placeholder for Proposal and Policy types.
# In a real implementation, these would be well-defined dataclasses.
Proposal = Any
Policy = Any


class SovereignFenceViolation(Exception):
    """Raised when a proposal violates a sovereign safety fence."""

    def __init__(self, reason_code: str, message: str):
        self.reason_code = reason_code
        self.message = message
        super().__init__(f"[{self.reason_code}] {self.message}")


@dataclass(frozen=True)
class FenceValidationResult:
    """The result of a fence validation check."""

    is_valid: bool
    violations: Sequence[SovereignFenceViolation]

    def to_digest_contribution(self) -> dict[str, Any]:
        """Returns a dictionary suitable for inclusion in a determinism digest."""
        return {
            "is_valid": self.is_valid,
            "violation_codes": sorted([v.reason_code for v in self.violations]),
        }


def validate(proposal: Proposal, policy: Policy) -> FenceValidationResult:
    """
    Validates a proposal against a sovereign policy fence.

    This is a hard boundary. It is not advisory. A validation failure here must
    block any state change (e.g., before a STAMP operation).

    Args:
        proposal: The proposed action or state change.
        policy: The sovereign policy to validate against.

    Returns:
        A FenceValidationResult indicating if the proposal is valid.
    """
    violations = []

    # Placeholder for actual validation logic.
    # For example, checking if the proposal tries to modify a protected file.
    # if proposal.path in policy.protected_paths:
    #     violations.append(
    #         SovereignFenceViolation(
    #             reason_code="PROTECTED_PATH_VIOLATION",
    #             message=f"Proposal attempts to modify protected path: {proposal.path}",
    #         )
    #     )

    return FenceValidationResult(is_valid=not violations, violations=violations)
