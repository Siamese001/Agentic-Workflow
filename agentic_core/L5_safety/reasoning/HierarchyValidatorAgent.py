"""
HierarchyValidatorAgent - L5 Pure Validator.

Scans for hierarchy violations (missing directories, misplaced files, depth
violations, orphaned files) without mutating the filesystem. Emits a
structured check dict consumed by heal_hierarchy_violations via HEALER_REGISTRY.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

CHECK_ID = "hierarchy_violations"


class HierarchyValidatorAgent:
    """L5 Certify-only validator for hierarchy compliance."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def scan(self, target_territory: str | None = None) -> dict[str, Any]:
        """Run HierarchyAgent.scan_root_violations() — pure scan, no mutations.

        Delegates to the same scan method used by execute_ssot.py Phase 3
        for violation detection.

        Args:
            target_territory: Optional territory to scope the scan.

        Returns:
            Raw scan results dict from HierarchyAgent.scan_root_violations().
        """
        from agentic_core.L5_safety.reasoning.HierarchyAgent import HierarchyAgent

        hierarchy = HierarchyAgent(project_root=self.project_root, healing_enabled=False)
        return hierarchy.scan_root_violations(target_territory=target_territory)

    def to_check_dict(self, target_territory: str | None = None) -> dict[str, Any]:
        """Return structured check dict for _invoke_healer dispatch."""
        scan_result = self.scan(target_territory=target_territory)
        violations_count = scan_result.get("violations_found", 0)
        if "violations" in scan_result and isinstance(scan_result["violations"], list):
            violations_count = len(scan_result["violations"])
        return {
            "check_id": CHECK_ID,
            "evidence": scan_result,
            "violations_count": violations_count,
            "territory": target_territory,
            "repo_root": str(self.project_root),
        }

    def run(self, target_territory: str | None = None) -> dict[str, Any]:
        """Alias for to_check_dict for orchestrator compatibility."""
        return self.to_check_dict(target_territory=target_territory)
