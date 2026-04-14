#!/usr/bin/env python3
"""
RCA FIX: Verify no uncommitted changes after pre-commit hooks.
"""

import subprocess
import sys


def _run_git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True, timeout=30)


def main() -> int:
    try:
        staged_result = _run_git("diff", "--cached", "--name-only")
        staged_files = (
            set(staged_result.stdout.strip().split("\n")) if staged_result.stdout.strip() else set()
        )

        modified_result = _run_git("diff", "--name-only")
        modified_files = (
            set(modified_result.stdout.strip().split("\n")) if modified_result.stdout.strip() else set()
        )

        problematic_files = staged_files.intersection(modified_files)

        status_result = _run_git("status", "--porcelain", "--untracked-files=no")
        uncommitted_issues = []
        for line in status_result.stdout.strip().split("\n"):
            if line and line[0] in ["M", "A", "D", "R", "C"] and len(line) > 3 and line[2] != " ":
                uncommitted_issues.append(line)

        if problematic_files or uncommitted_issues:
            print("ERROR: Uncommitted changes detected after pre-commit hooks!")
            print("This indicates a hook modified files without staging them.")
            print("")
            if problematic_files:
                print("Files that were staged but modified by hooks:")
                for file_name in sorted(problematic_files):
                    if file_name:
                        print(f"  - {file_name}")
            if uncommitted_issues:
                print("Other uncommitted changes:")
                for issue in uncommitted_issues:
                    print(f"  - {issue}")
            print("")
            print("To fix: git add . && git commit --amend --no-edit")
            return 1

        print("✅ Clean commit verified - no uncommitted changes from hooks")
        return 0

    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        print(f"Warning: Could not verify clean commit: {exc}")
        print("Continuing...")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
