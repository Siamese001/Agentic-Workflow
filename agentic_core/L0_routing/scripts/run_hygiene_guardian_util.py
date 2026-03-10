"""
Standalone script to run HygieneGuardianAgent on entire repo.
Reports findings before and after fixes.
"""

import os
import shutil
import sys
from pathlib import Path

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.config import ROOT_WHITELIST
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS

ALLOWED_ROOT_FOLDERS = set(ROOT_WHITELIST)
ARTIFACT_PATTERNS = ["*.heal_tmp", "*.temp", "*.tmp", ".pytest_cache", "__pycache__"]
IGNORE_FILES = {".gitkeep", ".git"}


def scan_temp_artifacts(root: Path) -> list[Path]:
    """Scan for temporary artifacts without removing them."""
    artifacts = []
    # Phase 6.7: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery_validator import get_data_files

    # Get all files with common artifact extensions
    for path in get_data_files(root, extensions=[".pyc", ".pyo", ".tmp", ".bak", ".swp"]):
        if ".git" not in path.parts:
            artifacts.append(path)
    return artifacts


def scan_empty_folders(root: Path) -> list[Path]:
    """Scan for empty folders without removing them."""
    empty_folders = []

    for root_folder in ALLOWED_ROOT_FOLDERS:
        root_path = root / root_folder
        if not root_path.exists():
            continue

        # Walk bottom-up
        for dirpath, _dirnames, _filenames in os.walk(root_path, topdown=False):
            _dirnames[:] = [d for d in _dirnames if d not in SOVEREIGN_EXCLUDED_FOLDERS]
            current_dir = Path(dirpath)

            # Skip .git and sovereign roots
            if ".git" in current_dir.parts:
                continue
            if current_dir.name in ALLOWED_ROOT_FOLDERS:
                continue

            # Check if folder is truly empty (ignoring .gitkeep)
            try:
                children = [x for x in current_dir.iterdir() if x.name not in IGNORE_FILES]
                if not children:
                    empty_folders.append(current_dir)
            except PermissionError:
                pass

    return empty_folders


def scan_folders_with_only_init(root: Path) -> list[Path]:
    """Scan for folders that only contain __init__.py (no other meaningful content)."""
    init_only_folders = []

    for root_folder in ALLOWED_ROOT_FOLDERS:
        root_path = root / root_folder
        if not root_path.exists():
            continue

        for dirpath, _dirnames, _filenames in os.walk(root_path, topdown=False):
            _dirnames[:] = [d for d in _dirnames if d not in SOVEREIGN_EXCLUDED_FOLDERS]
            current_dir = Path(dirpath)

            # Skip .git and sovereign roots
            if ".git" in current_dir.parts:
                continue
            if current_dir.name in ALLOWED_ROOT_FOLDERS:
                continue

            try:
                children = list(current_dir.iterdir())
                # Filter out .gitkeep and hidden files
                meaningful_children = [
                    x for x in children if x.name not in IGNORE_FILES and not x.name.startswith(".")
                ]

                # Check if only __init__.py exists (no subdirs, no other files)
                if len(meaningful_children) == 1:
                    only_child = meaningful_children[0]
                    if only_child.is_file() and only_child.name == "__init__.py":
                        init_only_folders.append(current_dir)
            except PermissionError:
                pass

    return init_only_folders


def remove_artifacts(artifacts: list[Path]) -> tuple[int, list[str]]:
    """Remove artifacts and return count and errors."""
    removed = 0
    errors = []

    for path in artifacts:
        try:
            if path.is_file():
                path.unlink()
                removed += 1
            elif path.is_dir():
                assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
                shutil.rmtree(path)
                removed += 1
        # guardian: allow-silent-swallow
        except Exception as e:
            errors.append(f"{path}: {e}")

    return removed, errors


def remove_empty_folders(folders: list[Path]) -> tuple[int, list[str]]:
    """Remove empty folders and return count and errors."""
    removed = 0
    errors = []

    # Sort by depth (deepest first) to handle nested empty folders
    sorted_folders = sorted(folders, key=lambda p: len(p.parts), reverse=True)

    for folder in sorted_folders:
        try:
            # Re-check if still empty (might have been parent of another empty folder)
            if folder.exists():
                children = [x for x in folder.iterdir() if x.name not in IGNORE_FILES]
                if not children:
                    folder.rmdir()
                    removed += 1
        # guardian: allow-silent-swallow
        except Exception as e:
            errors.append(f"{folder}: {e}")

    return removed, errors


def main():
    print("=" * 70)
    print("HYGIENE GUARDIAN AGENT - FULL REPO SCAN")
    print("=" * 70)

    project_root = PROJECT_ROOT
    print(f"\nProject Root: {project_root}")
    print(f"Allowed Root Folders: {sorted(ALLOWED_ROOT_FOLDERS)}")

    # === PHASE 1: SCAN (Before Fixes) ===
    print("\n" + "=" * 70)
    print("PHASE 1: INITIAL SCAN (Before Fixes)")
    print("=" * 70)

    # Scan for artifacts
    print("\n[1.1] Scanning for temporary artifacts...")
    artifacts = scan_temp_artifacts(project_root)
    print(f"      Found: {len(artifacts)} artifact(s)")
    for a in artifacts[:20]:  # Show first 20
        print(f"        - {a.relative_to(project_root)}")
    if len(artifacts) > 20:
        print(f"        ... and {len(artifacts) - 20} more")

    # Scan for empty folders
    print("\n[1.2] Scanning for empty folders...")
    empty_folders = scan_empty_folders(project_root)
    print(f"      Found: {len(empty_folders)} empty folder(s)")
    for f in empty_folders[:20]:
        print(f"        - {f.relative_to(project_root)}")
    if len(empty_folders) > 20:
        print(f"        ... and {len(empty_folders) - 20} more")

    # Scan for __init__.py only folders
    print("\n[1.3] Scanning for folders with only __init__.py...")
    init_only = scan_folders_with_only_init(project_root)
    print(f"      Found: {len(init_only)} folder(s) with only __init__.py")
    for f in init_only[:20]:
        print(f"        - {f.relative_to(project_root)}")
    if len(init_only) > 20:
        print(f"        ... and {len(init_only) - 20} more")

    # === PHASE 2: APPLY FIXES ===
    print("\n" + "=" * 70)
    print("PHASE 2: APPLYING FIXES")
    print("=" * 70)

    # Remove artifacts
    print("\n[2.1] Removing temporary artifacts...")
    artifacts_removed, artifact_errors = remove_artifacts(artifacts)
    print(f"      Removed: {artifacts_removed} artifact(s)")
    if artifact_errors:
        print(f"      Errors: {len(artifact_errors)}")
        for e in artifact_errors[:5]:
            print(f"        - {e}")

    # Remove empty folders
    print("\n[2.2] Removing empty folders...")
    folders_removed, folder_errors = remove_empty_folders(empty_folders)
    print(f"      Removed: {folders_removed} folder(s)")
    if folder_errors:
        print(f"      Errors: {len(folder_errors)}")
        for e in folder_errors[:5]:
            print(f"        - {e}")

    # === PHASE 3: RE-SCAN (After Fixes) ===
    print("\n" + "=" * 70)
    print("PHASE 3: VERIFICATION SCAN (After Fixes)")
    print("=" * 70)

    # Re-scan for artifacts
    print("\n[3.1] Re-scanning for temporary artifacts...")
    remaining_artifacts = scan_temp_artifacts(project_root)
    print(f"      Remaining: {len(remaining_artifacts)} artifact(s)")

    # Re-scan for empty folders
    print("\n[3.2] Re-scanning for empty folders...")
    remaining_empty = scan_empty_folders(project_root)
    print(f"      Remaining: {len(remaining_empty)} empty folder(s)")
    for f in remaining_empty:
        print(f"        - {f.relative_to(project_root)}")

    # Re-scan for __init__.py only folders
    print("\n[3.3] Re-scanning for folders with only __init__.py...")
    remaining_init_only = scan_folders_with_only_init(project_root)
    print(f"      Remaining: {len(remaining_init_only)} folder(s)")

    # === SUMMARY ===
    print("\n" + "=" * 70)
    print("SUMMARY REPORT")
    print("=" * 70)
    print(f"""
BEFORE FIXES:
  - Temporary artifacts: {len(artifacts)}
  - Empty folders: {len(empty_folders)}
  - __init__.py only folders: {len(init_only)}

FIXES APPLIED:
  - Artifacts removed: {artifacts_removed}
  - Empty folders removed: {folders_removed}

AFTER FIXES:
  - Remaining artifacts: {len(remaining_artifacts)}
  - Remaining empty folders: {len(remaining_empty)}
  - Remaining __init__.py only: {len(remaining_init_only)}

STATUS: {"✅ CLEAN" if len(remaining_artifacts) == 0 and len(remaining_empty) == 0 else "⚠️ ISSUES REMAIN"}
""")

    return {
        "before": {
            "artifacts": len(artifacts),
            "empty_folders": len(empty_folders),
            "init_only": len(init_only),
        },
        "fixed": {
            "artifacts_removed": artifacts_removed,
            "folders_removed": folders_removed,
        },
        "after": {
            "artifacts": len(remaining_artifacts),
            "empty_folders": len(remaining_empty),
            "init_only": len(remaining_init_only),
        },
        "artifacts_list": [str(a.relative_to(project_root)) for a in artifacts],
        "empty_folders_list": [str(f.relative_to(project_root)) for f in empty_folders],
        "init_only_list": [str(f.relative_to(project_root)) for f in init_only],
        "remaining_empty": [str(f.relative_to(project_root)) for f in remaining_empty],
    }


if __name__ == "__main__":
    main()
