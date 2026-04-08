#!/usr/bin/env python3
"""
Auto-stage hook fixes to prevent commit conflicts.

This hook runs after all other hooks to automatically stage any
modifications made by pre-commit hooks (like end-of-file-fixer,
mixed-line-ending, etc.) to prevent commit failures.
"""

import subprocess
import sys


def main():
    """Auto-stage any changes made by previous hooks."""
    try:
        # Check if there are any unstaged changes
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
        )

        unstaged_files = []
        for line in result.stdout.strip().split("\n"):
            if line and line[0] in " M":  # Modified but not staged
                unstaged_files.append(line[3:].strip())

        if unstaged_files:
            print(f"[auto-stage-hook-fixes] Auto-staging {len(unstaged_files)} files modified by hooks:")
            for f in unstaged_files[:10]:  # Show first 10
                print(f"  - {f}")
            if len(unstaged_files) > 10:
                print(f"  ... and {len(unstaged_files) - 10} more")

            # Stage all modifications
            subprocess.run(["git", "add", "-A"], check=True)
            print("[auto-stage-hook-fixes] All hook modifications staged")
        else:
            print("[auto-stage-hook-fixes] No hook modifications to stage")

        return 0

    except subprocess.CalledProcessError as e:
        print(f"[auto-stage-hook-fixes] Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[auto-stage-hook-fixes] Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
