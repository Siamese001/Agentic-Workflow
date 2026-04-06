#!/usr/bin/env python3
"""Compare archived files against current codebase to identify restoration candidates.

DEPRECATED (2026-04-06): The archives/ directory has been removed as part of
operational hygiene cleanup. This script is no longer functional since all
archived files have been deleted. Use git history for any restoration needs.
"""


def main():
    # DEPRECATED: archives/ directory removed 2026-04-06
    print("=" * 80)
    print("DEPRECATED: compare_archive_to_current_util.py")
    print("=" * 80)
    print("\nThe archives/ directory has been removed as part of operational hygiene cleanup.")
    print("This script is no longer functional.")
    print("\nFor file restoration needs, use git history:")
    print("  git log --follow -- <file_path>")
    print("  git checkout <commit_hash> -- <file_path>")
    print("\nExiting early.")
    return


if __name__ == "__main__":
    main()
