#!/usr/bin/env python3
"""
Pre-commit hook: Validate and process Windsurf rules

This hook ensures:
1. All ${VAR} references in rules are defined in _variables.yaml
2. _build/ directory is kept up-to-date with source rules

Install:
    cp tools/windsurf/pre_commit_rules.py .git/hooks/pre-commit-rules
    # Add to .git/hooks/pre-commit or run directly
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
HOOK_NAME = "windsurf-rules"


def main():
    print(f"[{HOOK_NAME}] Validating Windsurf rules variables...")

    # Step 1: Validate all variables are defined
    result = subprocess.run(  # noqa: S603 - trusted internal command
        [sys.executable, "tools/windsurf/preprocess_rules.py", "--validate"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        print(f"[{HOOK_NAME}] ❌ Validation failed:")
        print(result.stdout)
        print(result.stderr)
        print(f"\n[{HOOK_NAME}] Fix: Add missing variables to .windsurf/rules/_variables.yaml")
        return 1

    print(f"[{HOOK_NAME}] ✓ All variables valid")

    # Step 2: Check if _build/ is up-to-date
    print(f"[{HOOK_NAME}] Checking _build/ freshness...")
    result = subprocess.run(  # noqa: S603 - trusted internal command
        [sys.executable, "tools/windsurf/preprocess_rules.py", "--check"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        print(f"[{HOOK_NAME}] _build/ needs update, regenerating...")
        result = subprocess.run(  # noqa: S603 - trusted internal command
            [sys.executable, "tools/windsurf/preprocess_rules.py", "--process"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            print(f"[{HOOK_NAME}] ❌ Failed to regenerate _build/:")
            print(result.stderr)
            return 1

        print("[" + HOOK_NAME + "] ✓ Regenerated _build/ directory")
        print(f"[{HOOK_NAME}] ⚠️  You need to stage the updated files:")
        print("       git add .windsurf/rules/_build/")
        return 1  # Block commit so user can stage the changes

    print(f"[{HOOK_NAME}] ✓ _build/ is up-to-date")
    print(f"[{HOOK_NAME}] All checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
