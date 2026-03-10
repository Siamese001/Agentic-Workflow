#!/usr/bin/env python3
"""
RCA FIX: Verify no uncommitted changes after pre-commit hooks
Reference: UNCOMMITTED_CHANGES_RCA.md

This script checks if any files were modified by pre-commit hooks but not staged.
"""

import subprocess
import sys


def main():
    # Get list of files that were just modified (staged for commit)
    try:
        # Get staged files
        staged_result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
        )
        staged_files = (
            set(staged_result.stdout.strip().split("\n")) if staged_result.stdout.strip() else set()
        )

        # Get modified but unstaged files
        modified_result = subprocess.run(
            ["git", "diff", "--name-only"],
            capture_output=True,
            text=True,
        )
        modified_files = (
            set(modified_result.stdout.strip().split("\n")) if modified_result.stdout.strip() else set()
        )

        # Check if any staged files were also modified (means hook changed them after staging)
        problematic_files = staged_files.intersection(modified_files)

        # Also check for any new untracked files that might be hook outputs
        untracked_result = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            capture_output=True,
            text=True,
        )

        # Parse git status output for modified but unstaged files
        uncommitted_issues = []
        for line in untracked_result.stdout.strip().split("\n"):
            if line and line[0] in ["M", "A", "D", "R", "C"]:
                # File is modified/added/deleted but not staged
                if len(line) > 3 and line[2] != " ":
                    uncommitted_issues.append(line)

        if problematic_files or uncommitted_issues:
            print("ERROR: Uncommitted changes detected after pre-commit hooks!")
            print("This indicates a hook modified files without staging them.")
            print("")

            if problematic_files:
                print("Files that were staged but modified by hooks:")
                for f in problematic_files:
                    if f:
                        print(f"  - {f}")

            if uncommitted_issues:
                print("Other uncommitted changes:")
                for issue in uncommitted_issues:
                    print(f"  - {issue}")

            print("")
            print("To fix: git add . && git commit --amend --no-edit")
            sys.exit(1)
        else:
            print("✅ Clean commit verified - no uncommitted changes from hooks")

    except Exception as e:
        raise
        print(f"Warning: Could not verify clean commit: {e}")
        print("Continuing...")


if __name__ == "__main__":
    main()
