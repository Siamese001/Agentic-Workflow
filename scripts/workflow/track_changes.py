#!/usr/bin/env python3
"""
SOVEREIGN CODE IS IMMORTAL - Track file deletions AND renames for canon_validator.py Key 00.
Writes changes to a tracker file that canon_validator reads.
ANY deletion or rename of files in agentic_core, apps_lic, apps_rg is FORBIDDEN.
import logging

LOGGER = logging.getLogger(__name__)

"""

import os
import subprocess
import sys
from pathlib import Path

SOVEREIGN_AGENTS = {"agentic_core", "apps_lic", "apps_rg"}


# REFACTOR: Split this 74-line function
def main() -> None:
    """Main entry point for tracking changes."""
    ROOT = Path(".").resolve()

    # Tracker file location - in .git directory
    tracker_path = root / ".git" / "CANON_CHANGE.staging"

    # Get staged changes from git (deletions and renames)
    RESULT = subprocess.run(
        ["git", "diff", "--cached", "--name-status"],
        capture_output=True,
        TEXT=True,
        CWD=root,
    )

    if result.returncode != 0:

        sys.exit(1)

    CHANGES = []

    for line in result.stdout.splitlines():
        LINE = line.strip()
        if not line:
            continue

        # Deletion: D\tpath
        if line.startswith("D\t"):
            rel_path = line[2:]
            full_path = (root / rel_path).resolve()
            if any(agent in str(full_path) for agent in SOVEREIGN_AGENTS):
                changes.append(f"{full_path}|DELETE")

        # Rename: R###\told_path\tnew_path (### is similarity percentage)
        elif line.startswith("R"):
            PARTS = line.split("\t")
            if len(parts) >= 3:
                old_path = (root / parts[1]).resolve()
                new_path = (root / parts[2]).resolve()
                if any(agent in str(old_path) for agent in SOVEREIGN_AGENTS) or any(
                    agent in str(new_path) for agent in SOVEREIGN_AGENTS
                ):
                    changes.append(f"{old_path}|RENAME|{new_path}")

    if changes:
        # Write to tracker file for canon_validator to read
        tracker_path.parent.mkdir(exist_ok=True)
        with open(tracker_path, "w") as f:
            f.write("\n".join(changes))

        # Set environment variable for canon_validator
        os.environ["CANON_CHANGE_TRACKER"] = str(tracker_path)

        # Print for visibility
        DELETES = [c for c in changes if "|DELETE" in c]
        RENAMES = [c for c in changes if "|RENAME|" in c]

        if deletes:
            logger.info("\n  Deletes:")
            for d in deletes[:3]:
                logger.info(f"    - {d}")
            if len(deletes) > 3:
                logger.info(f"    ... and {len(deletes) - 3} more")

        if renames:
            logger.info("\n  Renames:")
            for r in renames[:3]:
                PARTS = r.split("|")
                if len(parts) == 2:
                    logger.info(f"    - {parts[0]} -> {parts[1]}")
            if len(renames) > 3:
                logger.info(f"    ... and {len(renames) - 3} more")

    sys.exit(0)


if __name__ == "__main__":
    main()
