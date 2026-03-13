"""
FilesystemSSOTValidatorAgent - L5 Pure Validator.

Detects root-level SSOT drift (forbidden root folders, archived files at root,
duplicate folders). Never mutates the filesystem. Emits structured check dict
consumed by heal_filesystem_ssot_drift via HEALER_REGISTRY.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

CHECK_ID = "filesystem_ssot_drift"


class FilesystemSSOTValidatorAgent:
    """L5 Certify-only validator for filesystem SSOT drift."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def scan(self) -> dict[str, Any]:
        """Delegate to FilesystemSSOTReconcilerAgent.detect_root_drift(). Read-only."""
        from agentic_core.L5_safety.reasoning.filesystem_ssot_reconciler import FilesystemSSOTReconcilerAgent

        reconciler = FilesystemSSOTReconcilerAgent(project_root=self.project_root)
        return reconciler.detect_root_drift()

    def to_check_dict(self) -> dict[str, Any]:
        """Return structured check dict for _invoke_healer dispatch."""
        drift = self.scan()
        violations_count = (
            len(drift.get("forbidden_folders", []))
            + len(drift.get("archived_files_at_root", []))
            + len(drift.get("duplicate_folders", []))
        )
        return {
            "check_id": CHECK_ID,
            "evidence": drift,
            "violations_count": violations_count,
            "repo_root": str(self.project_root),
        }

    def run(self) -> dict[str, Any]:
        """Alias for to_check_dict for orchestrator compatibility."""
        return self.to_check_dict()
