"""
Result Type Definitions - Standardized Return Objects

SSOT for all result types used across the agent architecture.
Ensures type safety and Liskov Substitution Principle compliance.

Created: Jan 2026 - MRO Safety Enhancement
"""

from typing import TypedDict


class HealResult(TypedDict):
    """
    Standardized return format for all healing operations.
    Ensures SSOT consistency across the orchestrator layer.

    Re-exported from healer_mixin for convenience.
    """

    violations_found: int
    violations_fixed: int
    status: str  # 'PASS', 'FAIL', 'ERROR', 'SKIPPED', 'UNKNOWN'
    errors: int
    skipped: int


class ValidationResult(TypedDict, total=False):
    """
    Standardized return format for all validation operations.
    Ensures type safety and LSP compliance for L5 Safety layer.

    Fields:
        is_safe: Whether the input passed all validation checks
        violations: List of violation types detected
        redacted_text: Text with PII/sensitive data redacted (optional)
        error: Error message if validation failed critically (optional)
        checks_performed: List of check names that were executed (optional)
        depth_exceeded: Flag if validation depth limit was reached (optional)
    """

    is_safe: bool
    violations: list[str]
    redacted_text: str | None
    error: str | None
    checks_performed: list[str] | None
    depth_exceeded: bool | None


__all__ = ["HealResult", "ValidationResult"]
