#!/usr/bin/env python3
"""
SSOT Path Guard (Smoke Detector)
Fast static path validation for pre-commit hooks.

This script validates that files match the structure_blueprint.py SSOT
without importing heavy dependencies. It uses simple string matching
for maximum speed (<1s execution time).

USAGE:
    python scripts/hooks/validate_paths.py [files...]

EXIT CODES:
    0 - All paths valid
    1 - Path violations detected
"""

import sys
from pathlib import Path

from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)

# Valid top-level directories from structure_blueprint.py SOVEREIGN_TERRITORIES
VALID_TERRITORIES = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES

# Valid subfolders for apps_* directories (depth 2)
APPS_VALID_SUBFOLDERS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS

# Forbidden patterns that indicate "Path Rot"
FORBIDDEN_PATTERNS = [
    "apps_shared/test_",  # No test files in apps_shared root
    "apps_rg/test_",  # No test files in apps_rg root
    "apps_lic/test_",  # No test files in apps_lic root
]


def validate_path(file_path: str) -> tuple[bool, str]:
    """
    Validate a single file path against SSOT rules.

    Returns:
        (is_valid, error_message)
    """
    path = Path(file_path)
    parts = path.parts

    if len(parts) < 2:
        # Root-level files are allowed (pyproject.toml, etc.)
        return True, ""

    # Check forbidden patterns
    posix_path = path.as_posix()
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in posix_path:
            return False, f"Forbidden pattern '{pattern}' detected in: {file_path}"

    # Check top-level territory
    territory = parts[0]
    if territory.startswith("."):
        # Hidden directories are generally allowed
        return True, ""

    if territory not in VALID_TERRITORIES:
        return False, f"Unknown territory '{territory}' in: {file_path}"

    # For apps_* directories, validate subfolder structure
    if territory.startswith("apps_"):
        if len(parts) >= 2:
            subfolder = parts[1]
            # Allow __init__.py and similar at depth 1
            if not subfolder.endswith(".py"):
                if subfolder not in APPS_VALID_SUBFOLDERS:
                    return False, f"Invalid subfolder '{subfolder}' in {territory}: {file_path}"

    return True, ""


def main() -> int:
    """Main entry point for pre-commit hook."""
    # Get files from command line args or stdin
    files = sys.argv[1:] if len(sys.argv) > 1 else []

    if not files:
        # No files to check
        return 0

    violations = []
    for file_path in files:
        is_valid, error = validate_path(file_path)
        if not is_valid:
            violations.append(error)

    if violations:
        print("\n" + "=" * 70)
        print("[SSOT PATH GUARD] STRUCTURAL VIOLATIONS DETECTED")
        print("=" * 70)
        for v in violations:
            print(f"  [X] {v}")
        print("=" * 70)
        print("\nFix: Move files to valid SSOT locations per structure_blueprint.py")
        print("=" * 70 + "\n")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
