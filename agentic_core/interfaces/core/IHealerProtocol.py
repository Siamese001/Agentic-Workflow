"""
IHealerProtocol - Sovereign Protocol for Healing Operations

Zero-Ambiguity Standard: Protocol interface for all healers
Category: PROTOCOL (Abstract interface contract)

This protocol defines the contract for any component that can heal violations
in the codebase. Implementations include L0RoutingBase and its subclasses.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class IHealerProtocol(Protocol):
    """
    Protocol defining the healing contract for sovereign agents.

    Any class implementing this protocol MUST provide:
    - heal_repository(): Main healing entry point
    - heal(): Single violation healing method
    """

    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Heal violations in the repository.

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, execute fixes (opposite of dry_run for clarity)
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            _call_path: Set of already-visited agents (cycle detection)
            **kwargs: Additional arguments for specific healers

        Returns:
            Dictionary with keys:
                - violations_found: Number of violations detected
                - violations_fixed: Number of violations fixed
                - errors: List of error messages
                - skipped: Number of skipped items
        """
        ...

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Heal a single violation.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        """
        ...
