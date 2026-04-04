"""Architecture Governor Validator Utility - Deterministic governance validation.

This module provides deterministic architecture governance validation previously
implemented in ArchitectureGovernorValidatorAgent. Converted from agent to utility
script as part of SCRIPT agent conversion (Micro-wave 9).

Usage:
    from agentic_core.L5_safety.utils.architecture_governor_validator_util import (
        ArchitectureGovernorValidator, validate_architecture_governance
    )

    # Validate governance
    result = validate_architecture_governance(Path("."))
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

Logger = logging.getLogger(__name__)


@dataclass
class GovernanceValidationResult:
    """Result of architecture governance validation."""

    check_id: str
    violations_count: int
    evidence: dict[str, Any]
    territory: str | None
    repo_root: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "check_id": self.check_id,
            "violations_count": self.violations_count,
            "evidence": self.evidence,
            "territory": self.territory,
            "repo_root": self.repo_root,
        }


CHECK_ID = "architecture_governance"


class ArchitectureGovernorValidator:
    """Deterministic architecture governance validator.

    This validator runs ArchitectureGovernorAgent in dry-run mode to detect
    architectural governance violations without mutating the codebase.
    """

    def __init__(self, project_root: Path) -> None:
        """Initialize validator.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root).resolve()

    def scan(self, target_territory: str | None = None) -> dict[str, Any]:
        """Run architecture governance scan in dry-run mode.

        Args:
            target_territory: Optional territory to scope the scan

        Returns:
            Raw governance report dict from heal_repository(dry_run=True)
        """
        try:
            from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import ArchitectureGovernorAgent

            agent = ArchitectureGovernorAgent(project_root=self.project_root)
            return agent.heal_repository(
                dry_run=True,
                execute=False,
                target_territory=target_territory,
            )
        except ImportError:
            Logger.error("ArchitectureGovernorAgent not available")
            return {
                "violations_found": 0,
                "violations_fixed": 0,
                "errors": 1,
                "error_message": "ArchitectureGovernorAgent not available",
            }

    def to_check_dict(self, target_territory: str | None = None) -> dict[str, Any]:
        """Return structured check dict for _invoke_healer dispatch.

        Args:
            target_territory: Optional territory to scope the scan

        Returns:
            Dictionary with check results for healer dispatch
        """
        scan_result = self.scan(target_territory=target_territory)
        violations_found = scan_result.get("violations_found", 0)

        return {
            "check_id": CHECK_ID,
            "evidence": scan_result,
            "violations_count": violations_found,
            "territory": target_territory,
            "repo_root": str(self.project_root),
        }

    def run(self, target_territory: str | None = None) -> dict[str, Any]:
        """Alias for to_check_dict for orchestrator compatibility.

        Args:
            target_territory: Optional territory to scope the scan

        Returns:
            Dictionary with check results
        """
        return self.to_check_dict(target_territory=target_territory)

    def validate(self, target_territory: str | None = None) -> GovernanceValidationResult:
        """Validate architecture governance.

        Args:
            target_territory: Optional territory to scope the scan

        Returns:
            GovernanceValidationResult with validation results
        """
        result = self.scan(target_territory)

        return GovernanceValidationResult(
            check_id=CHECK_ID,
            violations_count=result.get("violations_found", 0),
            evidence=result,
            territory=target_territory,
            repo_root=str(self.project_root),
        )


def validate_architecture_governance(
    project_root: str | Path,
    target_territory: str | None = None,
) -> GovernanceValidationResult:
    """Convenience function to validate architecture governance.

    Args:
        project_root: Project root directory
        target_territory: Optional territory to scope the scan

    Returns:
        GovernanceValidationResult with validation results
    """
    validator = ArchitectureGovernorValidator(Path(project_root))
    return validator.validate(target_territory)


def scan_governance(
    project_root: str | Path,
    target_territory: str | None = None,
) -> dict[str, Any]:
    """Convenience function to scan architecture governance.

    Args:
        project_root: Project root directory
        target_territory: Optional territory to scope the scan

    Returns:
        Raw governance report dict
    """
    validator = ArchitectureGovernorValidator(Path(project_root))
    return validator.scan(target_territory)
