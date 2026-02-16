#!/usr/bin/env python3
"""
Gatekeeper Lock - Pre-commit Security Hook

Protects critical infrastructure files from unauthorized modifications.
ArchivalGatekeeper.py is a PROTECTED file that requires explicit override.

USAGE:
    # As pre-commit hook (checks staged files)
    python scripts/security/gatekeeper_lock.py

    # With commit message file (for commit-msg stage)
    python scripts/security/gatekeeper_lock.py --commit-msg-filename .git/COMMIT_EDITMSG

BYPASS METHODS:
    1. Include '[SECURITY-OVERRIDE]' in commit message
    2. Set environment variable: GATEKEEPER_BYPASS=1
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

from agentic_core.utils.ast_fuzzy import normalize_path

# Protected files that require security override
PROTECTED_FILES = [
    "agentic_core/L5_safety/enforcement/ArchivalGatekeeper.py",
]

# Override token in commit message
OVERRIDE_TOKEN = "[SECURITY-OVERRIDE]"

# Environment variable for bypass
BYPASS_ENV_VAR = "GATEKEEPER_BYPASS"


def get_staged_files() -> list[str]:
    """Get list of staged files from git."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
        )
        return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
    except subprocess.CalledProcessError:
        return []


def get_commit_message(commit_msg_file: str | None) -> str:
    """Read commit message from file if provided."""
    if commit_msg_file and Path(commit_msg_file).exists():
        return Path(commit_msg_file).read_text(encoding="utf-8")
    return ""


def check_env_bypass() -> bool:
    """Check if bypass environment variable is set."""
    return os.environ.get(BYPASS_ENV_VAR, "").lower() in ("1", "true", "yes")


def check_commit_message_override(commit_message: str) -> bool:
    """Check if commit message contains override token."""
    return OVERRIDE_TOKEN in commit_message


def main() -> int:
    parser = argparse.ArgumentParser(description="Gatekeeper Lock - Protect critical files")
    parser.add_argument(
        "--commit-msg-filename",
        help="Path to commit message file (for commit-msg stage)",
    )
    args = parser.parse_args()

    # Check for bypass
    if check_env_bypass():
        print(f"[!] GATEKEEPER BYPASS: {BYPASS_ENV_VAR} environment variable set")
        return 0

    # Get staged files
    staged_files = get_staged_files()
    if not staged_files:
        return 0

    # Normalize paths for comparison
    staged_normalized = [normalize_path(f) for f in staged_files]
    protected_normalized = [normalize_path(f) for f in PROTECTED_FILES]

    # Check for protected file modifications
    protected_modified = []
    for protected in protected_normalized:
        for staged in staged_normalized:
            if staged == protected or staged.endswith(protected):
                protected_modified.append(protected)
                break

    if not protected_modified:
        return 0

    # Protected files are being modified - check for override
    commit_message = get_commit_message(args.commit_msg_filename)

    if check_commit_message_override(commit_message):
        print("[!] SECURITY OVERRIDE: Allowing modification of protected files")
        for f in protected_modified:
            print(f"   - {f}")
        return 0

    # No override - block the commit
    print("\n" + "=" * 70)
    print("[GATEKEEPER LOCK] COMMIT BLOCKED")
    print("=" * 70)
    print("\nThe following PROTECTED files are being modified:")
    for f in protected_modified:
        print(f"   [X] {f}")

    print("\n" + "-" * 70)
    print("ArchivalGatekeeper is a CRITICAL INFRASTRUCTURE file.")
    print("Unauthorized modifications could compromise system integrity.")
    print("-" * 70)

    print("\nTo proceed, use ONE of these methods:")
    print(f"\n  1. Add '{OVERRIDE_TOKEN}' to your commit message:")
    print(f'     git commit -m "Fix gatekeeper bug {OVERRIDE_TOKEN}"')
    print("\n  2. Set bypass environment variable:")
    print(f'     {BYPASS_ENV_VAR}=1 git commit -m "your message"')

    print("\n" + "=" * 70 + "\n")

    return 1


if __name__ == "__main__":
    sys.exit(main())
