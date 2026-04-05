#!/usr/bin/env python3
"""
Non-interactive branch merge utility
Merges governance_hardening into ADG with conflict resolution strategy
"""

import subprocess
import sys


def run_git(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run git command without terminal prompts"""
    result = subprocess.run(
        ["git"] + cmd,
        cwd="c:/Git/Agentic-Workflow",
        capture_output=True,
        text=True,
        env={"GIT_TERMINAL_PROMPT": "0"},
    )
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        sys.exit(result.returncode)
    return result


def main():
    print("Starting non-interactive merge...")

    # Ensure we're on ADG branch
    result = run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    current_branch = result.stdout.strip()
    print(f"Current branch: {current_branch}")

    if current_branch != "ADG":
        print("Switching to ADG branch...")
        run_git(["checkout", "ADG"])

    # Try merge with strategy to accept governance_hardening changes for conflicts
    print("Attempting merge with -X theirs strategy...")
    result = run_git(["merge", "-X", "theirs", "governance_hardening", "--no-edit"], check=False)

    if result.returncode == 0:
        print("✓ Merge completed successfully!")
        return 0

    print("Merge has conflicts. Analyzing...")

    # Get conflict list
    status_result = run_git(["diff", "--name-only", "--diff-filter=U"], check=False)
    conflicts = status_result.stdout.strip().split("\n") if status_result.stdout.strip() else []

    print(f"Found {len(conflicts)} conflicted files")

    if conflicts:
        print("\nConflicted files:")
        for f in conflicts[:10]:
            print(f"  - {f}")
        if len(conflicts) > 10:
            print(f"  ... and {len(conflicts) - 10} more")

    # Abort the merge
    print("\nAborting merge to reassess strategy...")
    run_git(["merge", "--abort"], check=False)

    return 1


if __name__ == "__main__":
    sys.exit(main())
