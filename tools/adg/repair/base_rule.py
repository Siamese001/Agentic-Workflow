"""Base rule class for ADG Repair Orchestrator.

All repair rules must inherit from BaseRepairRule and implement
the required abstract methods.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import Deficiency, FixResult


class BaseRepairRule(ABC):
    """Abstract base class for all repair rules.

    Repair rules define:
    1. What deficiency patterns they match
    2. How to determine if a fix can be applied
    3. How to apply the fix
    4. How to verify the fix worked

    Subclasses must implement:
    - match(): Check if this rule applies to a deficiency
    - can_fix(): Determine if the fix can be safely applied
    - apply_fix(): Apply the fix and return result
    - verify_fix(): Verify the fix was applied correctly
    """

    # Class attributes that subclasses should override
    rule_id: str = "base_rule"
    rule_name: str = "Base Repair Rule"
    rule_description: str = "Abstract base class for repair rules"
    rule_priority: int = 100  # Lower = higher priority

    def __init__(self):
        """Initialize the rule."""
        pass

    @abstractmethod
    def match(self, deficiency: Deficiency) -> bool:
        """Check if this rule applies to the given deficiency.

        Args:
            deficiency: The deficiency to check

        Returns:
            True if this rule can handle this deficiency
        """
        raise NotImplementedError

    @abstractmethod
    def can_fix(self, deficiency: Deficiency) -> tuple[bool, str]:
        """Determine if the fix can be safely applied.

        Args:
            deficiency: The deficiency to check

        Returns:
            Tuple of (can_fix, reason)
            - can_fix: True if fix can be applied
            - reason: Explanation if cannot fix
        """
        raise NotImplementedError

    @abstractmethod
    def apply_fix(self, deficiency: Deficiency) -> FixResult:
        """Apply the fix for this deficiency.

        Args:
            deficiency: The deficiency to fix

        Returns:
            FixResult with details of the fix
        """
        raise NotImplementedError

    @abstractmethod
    def verify_fix(self, deficiency: Deficiency, result: FixResult) -> bool:
        """Verify that the fix was applied correctly.

        Args:
            deficiency: The original deficiency
            result: The fix result to verify

        Returns:
            True if fix was verified successfully
        """
        raise NotImplementedError

    def get_info(self) -> dict:
        """Get information about this rule.

        Returns:
            Dictionary with rule metadata
        """
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "rule_description": self.rule_description,
            "rule_priority": self.rule_priority,
        }
