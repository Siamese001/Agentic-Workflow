"""
Gatekeeper Protection: Block commits that modify protected files.

This script prevents accidental modifications to critical infrastructure files
unless an explicit override is present in the commit message.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import get_validated_project_root


PROJECT_ROOT = get_validated_project_root()
PROTECTED_FILES = [
    "agentic_core/L5_safety/enforcement/ArchivalGatekeeper.py",
    "agentic_core/L5_safety/validators/decorators.py",
]
OVERRIDE_FLAG = "#gatekeeper-override"


def run_git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        check=check,
    )


def get_staged_files() -> list[str]:
    try:
        result = run_git("diff", "--cached", "--name-only")
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def get_commit_message() -> str:
    try:
        result = run_git("rev-parse", "--git-path", "COMMIT_EDITMSG")
        commit_msg_path = PROJECT_ROOT / result.stdout.strip()
        return (
            commit_msg_path.read_text(encoding="utf-8", errors="replace") if commit_msg_path.exists() else ""
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return ""


def find_modified_protected_files(staged_files: list[str]) -> list[str]:
    modified: list[str] = []
    for protected in PROTECTED_FILES:
        protected_path = Path(protected).as_posix()
        for staged in staged_files:
            staged_path = Path(staged).as_posix()
            if staged_path == protected_path or staged_path.endswith(protected_path):
                modified.append(protected)
                break
    return modified


def main() -> int:
    staged_files = get_staged_files()
    if not staged_files:
        return 0

    modified_protected = find_modified_protected_files(staged_files)
    if not modified_protected:
        return 0

    commit_message = get_commit_message()
    if OVERRIDE_FLAG in commit_message:
        print(f"\n[OK] Gatekeeper override detected: {OVERRIDE_FLAG}")
        print("   Allowing modifications to protected files:")
        for file_name in modified_protected:
            print(f"     - {file_name}")
        return 0

    print(f"\n{'=' * 70}")
    print("[GATEKEEPER PROTECTION] PROTECTED FILE MODIFICATION BLOCKED")
    print(f"{'=' * 70}")
    print("\nThe following protected files are being modified:")
    for file_name in modified_protected:
        print(f"  [X] {file_name}")
    print(f"\n{'=' * 70}")
    print("WHY THIS MATTERS:")
    print("  These files are critical infrastructure components:")
    print("  - ArchivalGatekeeper.py: The Executioner (safe file operations)")
    print("  - decorators.py: The Normalizer (@standard_heal schema)")
    print("\nTO PROCEED:")
    print(f"  Add '{OVERRIDE_FLAG}' to your commit message to override.")
    print("\nEXAMPLE:")
    print(f"  git commit -m 'Fix gatekeeper bug {OVERRIDE_FLAG}'")
    print(f"{'=' * 70}\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
