"""
ArchitectureGovernorValidatorAgent - L5 Pure Validator.

Detects architectural governance violations (import compliance, layer gravity,
naming) via StructureValidatorAgent without mutating the codebase. Emits a
structured check dict consumed by heal_architecture_governance via HEALER_REGISTRY.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

CHECK_ID = "architecture_governance"


class ArchitectureGovernorValidatorAgent:
    """L5 Certify-only validator for architectural governance."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def scan(self, target_territory: str | None = None) -> dict[str, Any]:
        """Run ArchitectureGovernorAgent.heal_repository in dry-run mode.

        Args:
            target_territory: Optional territory to scope the scan.

        Returns:
            Raw governance report dict from heal_repository(dry_run=True).
        """
        from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(project_root=self.project_root)
        return agent.heal_repository(dry_run=True, execute=False, target_territory=target_territory)

    def to_check_dict(self, target_territory: str | None = None) -> dict[str, Any]:
        """Return structured check dict for _invoke_healer dispatch."""
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
        """Alias for to_check_dict for orchestrator compatibility."""
        return self.to_check_dict(target_territory=target_territory)
