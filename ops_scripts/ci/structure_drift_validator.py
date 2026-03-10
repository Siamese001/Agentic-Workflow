"""Structure drift validator CLI for architectural integrity monitoring.

This module provides command-line validation of structure drift by comparing
the current codebase structure against a golden manifest.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from agentic_core.L5_safety.validators.structure_drift_validator import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    generate_structure_manifest,
    load_manifest,
)


def validate_structure_drift(golden_manifest_path: Path) -> bool:
    """Validate that the current structure matches the golden manifest.

    Args:
        golden_manifest_path: Path to the golden manifest file

    Returns:
        True if structure matches, False otherwise
    """
    if not golden_manifest_path.exists():
        print(f"ERROR: Golden manifest not found at {golden_manifest_path}")
        return False

    # Load golden manifest
    golden_manifest = load_manifest(golden_manifest_path)

    # Generate current manifest
    current_manifest = generate_structure_manifest()

    # Compare manifests
    if golden_manifest == current_manifest:
        print("PASS: Structure manifest matches golden")
        print(f"  hash={current_manifest['hash']}")
        return True

    # Find differences
    differences = []

    # Check directories
    golden_dirs = set(golden_manifest["directories"])
    current_dirs = set(current_manifest["directories"])

    if golden_dirs != current_dirs:
        added_dirs = current_dirs - golden_dirs
        removed_dirs = golden_dirs - current_dirs
        if added_dirs:
            differences.append(f"Added directories: {sorted(added_dirs)}")
        if removed_dirs:
            differences.append(f"Removed directories: {sorted(removed_dirs)}")

    # Check Python files
    golden_files = set(golden_manifest["python_files"])
    current_files = set(current_manifest["python_files"])

    if golden_files != current_files:
        added_files = current_files - golden_files
        removed_files = golden_files - current_files
        if added_files:
            differences.append(f"Added Python files: {sorted(added_files)}")
        if removed_files:
            differences.append(f"Removed Python files: {sorted(removed_files)}")

    # Check hash
    if golden_manifest["hash"] != current_manifest["hash"]:
        differences.append(
            f"Hash mismatch: golden={golden_manifest['hash']}, current={current_manifest['hash']}"
        )

    print("FAIL: Structure drift detected")
    for diff in differences:
        print(f"  - {diff}")

    return False


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Validate structure drift against golden manifest")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("artifacts/structure/structure_manifest.json"),
        help="Path to golden manifest file",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update golden manifest with current structure",
    )

    args = parser.parse_args()

    if args.update:
        # Update golden manifest
        manifest = generate_structure_manifest()
        from agentic_core.L5_safety.validators.structure_drift_validator import save_manifest

        save_manifest(manifest, args.manifest)
        print(f"Updated golden manifest at: {args.manifest}")
        print(f"New hash: {manifest['hash']}")
        return 0

    # Validate against golden manifest
    if validate_structure_drift(args.manifest):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
