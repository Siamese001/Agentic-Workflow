#!/usr/bin/env python3
"""
Strategic merge: Cherry-pick governance_hardening features into ADG
Avoids test file conflicts by only merging new ADG enhancement files
"""

import subprocess
import sys


def run_git(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run git command"""
    result = subprocess.run(["git"] + cmd, cwd="c:/Git/Agentic-Workflow", capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
    return result


def get_new_files_in_branch(branch: str, base: str) -> list[str]:
    """Get files added in branch that don't exist in base"""
    result = run_git(["diff", "--name-only", "--diff-filter=A", f"{base}..{branch}"])
    return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]


def main():
    print("Strategic merge: governance_hardening -> ADG")
    print("=" * 60)

    # Ensure on ADG branch
    run_git(["checkout", "ADG"])

    # Get files added only in governance_hardening
    new_files = get_new_files_in_branch("governance_hardening", "ADG")

    print(f"\nFiles added in governance_hardening: {len(new_files)}")

    # Filter for ADG enhancement files
    adg_files = [f for f in new_files if "adg" in f.lower() and ("analysis" in f or "enhancement" in f)]

    print(f"ADG-related new files: {len(adg_files)}")
    for f in adg_files:
        print(f"  + {f}")

    if not adg_files:
        print("\nNo new ADG files to merge. Checking modified files...")

        # Get modified files
        result = run_git(["diff", "--name-only", "ADG...governance_hardening"])
        modified = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]

        adg_modified = [
            f
            for f in modified
            if "adg" in f.lower() and not f.startswith("tests/") and not f.startswith("artifacts/")
        ]

        print(f"\nADG source files modified in governance_hardening: {len(adg_modified)}")
        for f in adg_modified:
            print(f"  ~ {f}")

        if adg_modified:
            print("\nStrategy: Cherry-pick specific commits with ADG enhancements")

            # Get commits that touch ADG files
            result = run_git(
                [
                    "log",
                    "--oneline",
                    "--no-merges",
                    "ADG..governance_hardening",
                    "--",
                    "agentic_core/adg/",
                    "tools/generate_full_adg.py",
                ]
            )

            commits = [line.split()[0] for line in result.stdout.strip().split("\n") if line.strip()]

            print(f"\nCommits touching ADG files: {len(commits)}")
            for commit in commits:
                result = run_git(["log", "-1", "--oneline", commit])
                print(f"  {result.stdout.strip()}")

            return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
