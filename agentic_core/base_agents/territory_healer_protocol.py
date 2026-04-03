"""
TerritoryHealerProtocol - Standardized interface for territory-level healing agents.

This protocol defines the simplified interface that all healing agents must implement
to support territory-level healing without bypasses or complex workarounds.
"""

from typing import Protocol, Any
from pathlib import Path
from dataclasses import dataclass


@dataclass
class HealingContext:
    """Simplified context for healing operations."""
    heal: bool  # If True, apply mutations. If False, dry-run only.
    project_root: Path
    verbose: bool = False

    # Optional: specific configuration for this healing run
    config: dict[str, Any] | None = None


@dataclass
class Violation:
    """Standardized violation representation."""
    type: str
    path: str
    message: str
    severity: str = "ERROR"  # ERROR, WARNING, INFO
    details: dict[str, Any] | None = None


@dataclass
class ScanResult:
    """Result from scanning a territory for violations."""
    territory: str
    violations_found: int
    violations: list[Violation]
    scan_metadata: dict[str, Any] | None = None


@dataclass
class HealingResult:
    """Result from healing a territory."""
    territory: str
    agent_name: str
    violations_found: int
    violations_fixed: int
    actions_taken: list[dict[str, Any]]
    errors: list[str]
    success: bool
    dry_run: bool


class TerritoryHealerProtocol(Protocol):
    """
    Protocol for agents that can heal territories.

    All healing agents must implement this interface for territory-level
    healing to work consistently without bypasses.
    """

    @property
    def agent_name(self) -> str:
        """Return the canonical name of this agent."""
        ...

    def can_handle(self, territory: str) -> bool:
        """
        Check if this agent can handle the given territory.

        Args:
            territory: The territory name (e.g., "tests", "agentic_core", "apps_eval")

        Returns:
            True if this agent can scan/heal this territory
        """
        ...

    def scan_territory(self, territory: str) -> ScanResult:
        """
        Scan a territory for violations without making any changes.

        Args:
            territory: The territory to scan

        Returns:
            ScanResult with violations found
        """
        ...

    def heal_territory(self, territory: str, context: HealingContext) -> HealingResult:
        """
        Heal violations in a territory.

        This is the primary healing method that should:
        1. Scan for violations
        2. Apply fixes if context.heal is True
        3. Return detailed results

        Args:
            territory: The territory to heal
            context: HealingContext with heal flag and configuration

        Returns:
            HealingResult with details of actions taken
        """
        ...
