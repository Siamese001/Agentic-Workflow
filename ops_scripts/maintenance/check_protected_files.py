"""
Gatekeeper Protection: Block commits that modify protected files

This script prevents accidental modifications to critical infrastructure files
like ArchivalGatekeeper.py unless an explicit override is present in the commit message.

PROTECTED FILES:
    - agentic_core/L5_safety/enforcement/ArchivalGatekeeper.py (The Executioner)
    - agentic_core/L5_safety/validators/decorators.py (The Normalizer)

OVERRIDE:
    Include '#gatekeeper-override' in your commit message to bypass protection.

USAGE:
    python scripts/maintenance/check_protected_files.py

EXIT CODES:
    0 - No protected files modified OR override present
    1 - Protected files modified without override
"""

import subprocess
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)

PROTECTED_FILES = [
    "agentic_core/L5_safety/enforcement/ArchivalGatekeeper.py",
    "agentic_core/L5_safety/validators/decorators.py",
]
OVERRIDE_FLAG = "#gatekeeper-override"


def get_staged_files() -> list[str]:
    """Get list of files staged for commit."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, check=True
        )
        return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
    except subprocess.CalledProcessError:
        return []


def get_commit_message() -> str:
    """Get the commit message if available."""
    try:
        commit_msg_file = Path(".git/COMMIT_EDITMSG")
        if commit_msg_file.exists():
            return commit_msg_file.read_text()
        return ""
    except (
        OSError,
        UnicodeDecodeError,
    ):  # guardian: File operations with encoding need error-specific handling
        return ""


def main():
    staged_files = get_staged_files()
    if not staged_files:
        sys.exit(0)
    modified_protected = []
    for protected in PROTECTED_FILES:
        protected_path = Path(protected).as_posix()
        for staged in staged_files:
            staged_path = Path(staged).as_posix()
            if staged_path == protected_path or staged_path.endswith(protected_path):
                modified_protected.append(protected)
                break
    if not modified_protected:
        sys.exit(0)
    commit_message = get_commit_message()
    if OVERRIDE_FLAG in commit_message:
        print(f"\n[OK] Gatekeeper override detected: {OVERRIDE_FLAG}")
        print("   Allowing modifications to protected files:")
        for f in modified_protected:
            print(f"     - {f}")
        sys.exit(0)
    print(f"\n{'=' * 70}")
    print("[GATEKEEPER PROTECTION] PROTECTED FILE MODIFICATION BLOCKED")
    print(f"{'=' * 70}")
    print("\nThe following protected files are being modified:")
    for f in modified_protected:
        print(f"  [X] {f}")
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
    sys.exit(1)


if __name__ == "__main__":
    main()
