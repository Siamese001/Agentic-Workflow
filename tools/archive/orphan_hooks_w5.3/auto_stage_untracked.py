#!/usr/bin/env python3
"""Auto-stage untracked files before commit.

Pre-commit hook that automatically stages untracked files to prevent
the "untracked files never committed" issue.

Exclusions:
- Files matching .gitignore patterns
- ADG archive files (*.gz in artifacts/adg/_archive/)
- Temporary files and build artifacts
"""

import subprocess
import sys


def get_untracked_files() -> list[str]:
    """Get list of untracked files from git ls-files."""
    # Use git ls-files to get untracked files without quote escaping
    result = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        capture_output=True,
        text=True,
        check=True,
    )

    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def should_auto_stage(filepath: str) -> bool:
    """Determine if file should be auto-staged.

    Excludes:
    - ADG archive files (compressed backups)
    - Temporary files
    - Build artifacts
    """
    # Exclude ADG archives (they're intentionally local-only)
    if "artifacts/adg/_archive/" in filepath:
        return False

    # Exclude compressed files in ADG directory
    if filepath.endswith(".gz") and "artifacts/adg/" in filepath:
        return False

    # Exclude temporary files
    temp_patterns = ["_temp_", "tmp", ".tmp", "_out_", "_capture_"]
    if any(pattern in filepath for pattern in temp_patterns):
        return False

    # Exclude build artifacts
    if "__pycache__" in filepath or ".pytest_cache" in filepath:
        return False

    # Auto-stage everything else (documentation, code, etc.)
    return True


def main() -> int:
    """Auto-stage untracked files that should be version controlled."""
    untracked = get_untracked_files()

    if not untracked:
        return 0

    files_to_stage = [f for f in untracked if should_auto_stage(f)]

    if not files_to_stage:
        return 0

    # Stage the files
    print(f"[auto-stage] Staging {len(files_to_stage)} untracked file(s):")
    for filepath in files_to_stage:
        print(f"  + {filepath!s}")

    subprocess.run(
        ["git", "add"] + files_to_stage,
        check=True,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
