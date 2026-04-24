#!/usr/bin/env python3
"""
Unified Auto-Stage Hook

Combines auto-stage-untracked and auto-stage-hook-fixes into a single hook.
Stages untracked files (with exclusions) and any modifications made by
previous hooks to prevent commit conflicts.

Exclusions (from auto-stage-untracked):
- ADG archive files (*.gz in artifacts/adg/_archive/)
- Temporary files and build artifacts
"""

import subprocess
import sys


def get_untracked_files() -> list[str]:
    """Get list of untracked files from git ls-files."""
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
    - ADG archives (they're intentionally local-only)
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


def get_unstaged_files() -> list[str]:
    """Get list of unstaged modified files."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    )

    unstaged_files = []
    for line in result.stdout.strip().split("\n"):
        if line and line.startswith(" M "):
            path = line[3:].strip()
            # Handle cases where paths with spaces are quoted
            if path.startswith('"') and path.endswith('"'):
                path = path[1:-1]
            unstaged_files.append(path)
    return unstaged_files


def main() -> int:
    """Auto-stage untracked files and hook modifications."""
    try:
        # Stage untracked files that should be version controlled
        untracked = get_untracked_files()
        files_to_stage = [f for f in untracked if should_auto_stage(f)]

        if files_to_stage:
            print(f"[auto-stage] Staging {len(files_to_stage)} untracked file(s):")
            for filepath in files_to_stage[:10]:  # Show first 10
                print(f"  + {filepath!s}")
            if len(files_to_stage) > 10:
                print(f"  ... and {len(files_to_stage) - 10} more")

        # Stage unstaged modifications (hook fixes)
        unstaged = get_unstaged_files()
        if unstaged:
            print(f"[auto-stage] Staging {len(unstaged)} modified file(s):")
            for f in unstaged[:10]:  # Show first 10
                print(f"  - {f}")
            if len(unstaged) > 10:
                print(f"  ... and {len(unstaged) - 10} more")

        # Stage everything at once
        if files_to_stage or unstaged:
            print("[auto-stage] Staging all new and modified files.")
            subprocess.run(["git", "add", "."], check=True)
            print("[auto-stage] Staging complete.")
        else:
            print("[auto-stage] No files to stage")

        return 0

    except subprocess.CalledProcessError as e:
        print(f"[auto-stage] Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
        print(f"[auto-stage] Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
