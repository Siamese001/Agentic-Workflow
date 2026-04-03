"""SSOT Folder Cleanup Agent - Backward compatibility shim.

DEPRECATED: This agent has been converted to a utility script.
Use agentic_core.L0_routing.utils.ssot_folder_cleanup_util instead.

This module maintains backward compatibility by delegating to the utility.
Will be removed in a future release.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L0_routing.utils.ssot_folder_cleanup_util import (
    CleanupStats,
)
from agentic_core.L0_routing.utils.ssot_folder_cleanup_util import (
    cleanup_repository as _cleanup_repository,
)
from agentic_core.L0_routing.utils.ssot_folder_cleanup_util import (
    delete_empty_folders as _delete_empty_folders,
)
from agentic_core.L0_routing.utils.ssot_folder_cleanup_util import (
    find_non_approved_files as _find_non_approved_files,
)
from agentic_core.L0_routing.utils.ssot_folder_cleanup_util import (
    move_file_to_ssot as _move_file_to_ssot,
)
from agentic_core.L0_routing.utils.ssot_folder_cleanup_util import (
    update_imports_for_moved_file as _update_imports,
)


class SSOTFolderCleanupAgent(SovereignBaseAgent):
    """
    DEPRECATED: SSOT Folder Cleanup Agent - now delegates to ssot_folder_cleanup_util.

    This class is maintained for backward compatibility only.
    New code should use agentic_core.L0_routing.utils.ssot_folder_cleanup_util directly.
    """

    def __init__(self, project_root: Path | None = None, dry_run: bool = True):
        """Initialize SSOTFolderCleanupAgent (deprecated, use ssot_folder_cleanup_util instead)."""
        super().__init__(name="SSOTFolderCleanupAgent", layer="L0")

        warnings.warn(
            "SSOTFolderCleanupAgent is deprecated. Use agentic_core.L0_routing.utils.ssot_folder_cleanup_util instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.project_root = project_root or Path.cwd()
        self.dry_run = dry_run
        self.stats = CleanupStats()

    def find_non_approved_files(self) -> list[Path]:
        """Find all Python files in non-SSOT-approved folders."""
        return _find_non_approved_files(self.project_root)

    def move_file_to_ssot(self, source_path: Path, target_path: str) -> bool:
        """Move a file to its SSOT-approved location."""
        return _move_file_to_ssot(source_path, target_path, self.dry_run)

    def update_imports_for_moved_file(self, old_path: Path, new_path: Path) -> int:
        """Update all imports referencing a moved file."""
        return _update_imports(old_path, new_path, self.dry_run)

    def delete_empty_folders(self, start_path: Path | None = None) -> int:
        """Delete empty non-SSOT-approved folders."""
        return _delete_empty_folders(start_path or self.project_root, self.dry_run)

    def cleanup_repository(self) -> dict[str, Any]:
        """Execute full SSOT folder cleanup."""
        return _cleanup_repository(self.project_root, self.dry_run)

    def preview_cleanup(self) -> dict[str, Any]:
        """Preview cleanup without making changes."""
        return _cleanup_repository(self.project_root, dry_run=True)

    def execute_cleanup(self) -> dict[str, Any]:
        """Execute cleanup with actual file changes."""
        return _cleanup_repository(self.project_root, dry_run=False)

    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> dict[str, Any]:
        """Autonomous healing method (Canon Key 51 compliance)."""
        result = _cleanup_repository(self.project_root, dry_run=dry_run)
        return {
            "violations_found": result.get("non_approved_files", 0),
            "violations_fixed": result.get("files_moved", 0),
            "errors": result.get("errors", 0),
            "dry_run": dry_run,
            "details": result,
        }

    def is_path_ssot_approved(self, path: Path) -> bool:
        """Check if a path is in an SSOT-approved location."""
        from agentic_core.L0_routing.utils.ssot_folder_cleanup_util import is_path_ssot_approved

        return is_path_ssot_approved(path, self.project_root)

    def triage_file(self, file_path: Path) -> dict[str, Any]:
        """Determine where a file should go."""
        from agentic_core.L0_routing.utils.ssot_folder_cleanup_util import triage_file

        return triage_file(file_path, self.project_root)
