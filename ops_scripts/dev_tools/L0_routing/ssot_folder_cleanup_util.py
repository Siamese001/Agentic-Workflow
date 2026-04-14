"""SSOT Folder Cleanup Utility - Deterministic folder cleanup operations.

This module provides deterministic file cleanup functionality previously
implemented in SSOTFolderCleanupAgent. Converted from agent to utility script
as part of Phase 2 optimization (Wave 5 Micro-Wave 2).

Usage:
    from ops_scripts.dev_tools.L0_routing.ssot_folder_cleanup_util import (
        cleanup_repository, find_non_approved_files, move_file_to_ssot
    )

    # Run cleanup
    results = cleanup_repository(project_root=Path("."), dry_run=True)
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    ARCHIVES_DIR,
    REPORTS_DIR,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from tqdm import tqdm

Logger = logging.getLogger(__name__)


@dataclass
class CleanupStats:
    """Statistics for cleanup operations."""

    files_scanned: int = 0
    files_moved: int = 0
    files_archived: int = 0
    imports_updated: int = 0
    folders_deleted: int = 0
    errors: int = 0


def find_non_approved_files(project_root: Path) -> list[Path]:
    """Find all files in non-SSOT-approved folders."""
    non_approved_files: list[Path] = []

    for root, dirs, files in tqdm(os.walk(project_root), desc="Processing", unit="item"):
        root_path = Path(root)

        # Skip approved folders
        if any(approved in str(root_path) for approved in [AGENTIC_CORE_DIR, ARCHIVES_DIR, REPORTS_DIR]):
            continue

        # Skip excluded folders
        if any(excluded in str(root_path) for excluded in SOVEREIGN_EXCLUDED_FOLDERS):
            continue

        for file_name in files:
            if not file_name.startswith("."):  # Skip hidden files
                file_path = root_path / file_name
                non_approved_files.append(file_path)

    return non_approved_files


def triage_file(file_path: Path, project_root: Path) -> dict[str, Any]:
    """Triage a file to determine appropriate action."""
    # Basic triage logic - can be extended based on file type/content
    ext = file_path.suffix.lower()

    # Python files -> likely belong in agentic_core
    if ext == ".py":
        return {
            "action": "MOVE",
            "target_path": "agentic_core",
            "reason": "Python file belongs in agentic_core",
            "confidence": 0.8,
        }

    # Markdown files -> likely belong in docs
    if ext == ".md":
        return {
            "action": "MOVE",
            "target_path": "docs",
            "reason": "Documentation file belongs in docs",
            "confidence": 0.9,
        }

    # JSON/Config files -> evaluate based on content
    if ext in [".json", ".yaml", ".yml", ".toml"]:
        return {
            "action": "MOVE",
            "target_path": "config",
            "reason": "Configuration file belongs in config",
            "confidence": 0.7,
        }

    # Test files -> tests directory
    if "test" in file_path.name.lower():
        return {
            "action": "MOVE",
            "target_path": "tests",
            "reason": "Test file belongs in tests",
            "confidence": 0.9,
        }

    # Low confidence -> archive for manual review
    return {
        "action": "ARCHIVE",
        "target_path": None,
        "reason": "Unclear destination - archive for review",
        "confidence": 0.3,
    }


def move_file_to_ssot(
    source: Path,
    target_dir: str,
    project_root: Path,
    dry_run: bool = True,
) -> bool:
    """Move a file to SSOT-approved location."""
    target_path = project_root / target_dir / source.name

    if dry_run:
        Logger.info(f"[DRY RUN] Would move: {source} -> {target_path}")
        return True

    try:
        assert_no_persistent_write("L0", "shutil.mutate")
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Use os.rename for atomic move
        os.rename(str(source), str(target_path))
        Logger.info(f"Moved: {source} -> {target_path}")
        return True
    except OSError as e:
        Logger.error(f"Failed to move {source}: {e}")
        return False


def update_imports_for_moved_file(
    old_path: Path,
    new_path: Path,
    project_root: Path,
    dry_run: bool = True,
) -> int:
    """Update imports referencing a moved file.

    Returns:
        Number of imports updated
    """
    updates = 0

    # Find all Python files that might import the moved file
    # Use as_posix() for proper cross-platform path normalization
    rel_old = old_path.relative_to(project_root)
    old_module = str(rel_old.as_posix()).replace("/", ".")
    old_module = old_module.replace(".py", "")

    rel_new = new_path.relative_to(project_root)
    new_module = str(rel_new.as_posix()).replace("/", ".")
    new_module = new_module.replace(".py", "")

    for py_file in tqdm(project_root.rglob("*.py"), desc="Processing", unit="item"):
        if py_file == old_path or py_file == new_path:
            continue

        try:
            content = py_file.read_text(encoding="utf-8")

            # Simple import pattern replacement
            # This is a simplified version - real implementation would use AST
            updated_content = content

            # Replace 'from old_module import ...'
            pattern = rf"from\s+{re.escape(old_module)}\s+import"
            if re.search(pattern, content):
                if not dry_run:
                    updated_content = re.sub(pattern, f"from {new_module} import", updated_content)
                    py_file.write_text(updated_content, encoding="utf-8")
                updates += 1
                Logger.info(f"Updated imports in: {py_file}")

        except Exception as e:
            Logger.warning(f"Failed to update imports in {py_file}: {e}")

    return updates


def delete_empty_folders(
    project_root: Path,
    dry_run: bool = True,
) -> int:
    """Delete empty non-approved folders.

    Returns:
        Number of folders deleted
    """
    deleted_count = 0

    for root, dirs, files in tqdm(os.walk(str(project_root), topdown=False), desc="Processing", unit="item"):
        root_path = Path(root)

        # Skip approved folders
        if any(approved in str(root_path) for approved in [AGENTIC_CORE_DIR, ARCHIVES_DIR, REPORTS_DIR]):
            continue

        # Check if folder is now empty
        if not any(root_path.iterdir()):
            if dry_run:
                Logger.info(f"[DRY RUN] Would delete empty folder: {root_path}")
            else:
                try:
                    root_path.rmdir()
                    Logger.info(f"Deleted empty folder: {root_path}")
                    deleted_count += 1
                except OSError as e:
                    Logger.warning(f"Failed to delete folder {root_path}: {e}")

    return deleted_count


def cleanup_repository(
    project_root: Path | None = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Execute full SSOT folder cleanup.

    Args:
        project_root: Project root path (defaults to current directory)
        dry_run: If True, only report actions without executing

    Returns:
        Summary of cleanup operations
    """
    project_root = project_root or Path(".")
    Logger.info(f"Starting SSOT folder cleanup (dry_run={dry_run})")

    stats = CleanupStats()

    non_approved_files = find_non_approved_files(project_root)
    stats.files_scanned = len(non_approved_files)
    Logger.info(f"Found {len(non_approved_files)} files in non-approved locations")

    move_plan: list[dict[str, Any]] = []

    for file_path in tqdm(non_approved_files, desc="Processing", unit="item"):
        triage = triage_file(file_path, project_root)

        if triage["action"] == "MOVE" and triage["target_path"]:
            move_plan.append(
                {
                    "source": file_path,
                    "target": triage["target_path"],
                    "reason": triage["reason"],
                    "confidence": triage["confidence"],
                }
            )
        elif triage["action"] == "ARCHIVE":
            move_plan.append(
                {
                    "source": file_path,
                    "target": "archives/ssot_cleanup",
                    "reason": triage["reason"],
                    "confidence": triage["confidence"],
                    "archive": True,
                }
            )
        else:
            Logger.info(f"Skipping {file_path}: {triage['action']} - {triage['reason']}")

    # Execute moves
    for plan in tqdm(move_plan, desc="Processing", unit="item"):
        source = plan["source"]
        target = plan["target"]

        success = move_file_to_ssot(source, target, project_root, dry_run)

        if success:
            if plan.get("archive"):
                stats.files_archived += 1
            else:
                stats.files_moved += 1

            if not dry_run:
                new_path = project_root / target / source.name
                updates = update_imports_for_moved_file(source, new_path, project_root, dry_run)
                stats.imports_updated += updates

    # Delete empty folders
    deleted_folders = delete_empty_folders(project_root, dry_run)
    stats.folders_deleted = deleted_folders

    summary = {
        "dry_run": dry_run,
        "files_scanned": stats.files_scanned,
        "non_approved_files": len(non_approved_files),
        "files_moved": stats.files_moved,
        "files_archived": stats.files_archived,
        "imports_updated": stats.imports_updated,
        "folders_deleted": stats.folders_deleted,
        "errors": stats.errors,
        "move_plan": move_plan if dry_run else None,
    }

    Logger.info(f"SSOT cleanup complete: {summary}")
    return summary


def preview_cleanup(project_root: Path | None = None) -> dict[str, Any]:
    """Preview cleanup without making changes.

    Returns:
        Preview of what would be changed
    """
    return cleanup_repository(project_root, dry_run=True)


def execute_cleanup(project_root: Path | None = None) -> dict[str, Any]:
    """Execute cleanup with actual file changes.

    Returns:
        Summary of changes made
    """
    return cleanup_repository(project_root, dry_run=False)


def heal_repository(
    project_root: Path | None = None,
    dry_run: bool = True,
    execute: bool = False,
    **kwargs: Any,
) -> dict[str, Any]:
    """Autonomous healing method (Canon Key 51 compliance).

    Args:
        project_root: Project root path
        dry_run: If True, only report violations without fixing
        execute: If True, apply fixes

    Returns:
        Dict with healing summary
    """
    actual_dry_run = dry_run if not execute else False
    result = cleanup_repository(project_root, dry_run=actual_dry_run)

    return {
        "violations_found": result.get("non_approved_files", 0),
        "violations_fixed": result.get("files_moved", 0),
        "errors": result.get("errors", 0),
        "skipped": 0,
    }


def heal(violation: dict[str, Any]) -> dict[str, Any]:
    """Heal SSOT folder violations.

    Args:
        violation: Dictionary containing violation details with keys:
            - type: Type of violation (orphan, misplaced)
            - path: Path to the violating file
            - target_path: Suggested target path

    Returns:
        Dictionary with healing results following standard_heal format.
    """
    path = violation.get("path", "")
    target_path = violation.get("target_path", "")

    Logger.info(f"[SSOT_CLEANUP] Healing file location: {path}")

    if path and target_path:
        try:
            source = Path(path)
            if source.exists():
                success = move_file_to_ssot(
                    source,
                    target_path,
                    project_root=source.parent,
                    dry_run=False,
                )
                if success:
                    return {
                        "violations_fixed": 1,
                        "violations_found": 1,
                        "errors": 0,
                        "skipped": 0,
                    }
        except (ValueError, TypeError, RuntimeError) as e:
            Logger.error(f"[SSOT_CLEANUP] Failed to heal: {e}")
            return {
                "violations_fixed": 0,
                "violations_found": 1,
                "errors": 1,
                "skipped": 0,
            }

    return {
        "violations_fixed": 0,
        "violations_found": 1,
        "errors": 0,
        "skipped": 1,
    }


def main() -> dict[str, Any]:
    """Main entry point for SSOT Folder Cleanup Utility."""
    import argparse

    parser = argparse.ArgumentParser(description="SSOT Folder Cleanup Utility")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute cleanup (default: dry-run)",
    )
    parser.add_argument(
        "--project-root",
        type=str,
        default=".",
        help="Project root path",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    project_root = Path(args.project_root)
    dry_run = not args.execute

    results = cleanup_repository(project_root, dry_run=dry_run)

    print("\n" + "=" * 70)
    print("📊 SSOT FOLDER CLEANUP SUMMARY")
    print("=" * 70)
    print(f"Files scanned: {results['files_scanned']}")
    print(f"Files moved: {results['files_moved']}")
    print(f"Files archived: {results['files_archived']}")
    print(f"Imports updated: {results['imports_updated']}")
    print(f"Folders deleted: {results['folders_deleted']}")
    print(f"Errors: {results['errors']}")
    print(f"\nMode: {'DRY RUN' if results['dry_run'] else 'EXECUTE'}")

    return results


if __name__ == "__main__":
    main()
