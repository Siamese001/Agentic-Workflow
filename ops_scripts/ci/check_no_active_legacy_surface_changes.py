#!/usr/bin/env python3
"""Block new active Windsurf workflow artifacts.

The repository is Cursor-native. Historical Windsurf material may remain only in
explicit archive/compatibility locations, and existing `.windsurf/**` files are
not an authoring surface. This staged-file gate prevents fresh edits from
reintroducing `.windsurf` as a live SSOT.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

BLOCKED_PREFIXES = (
    ".windsurf/plans/",
    ".windsurf/skills/",
    ".windsurf/workflows/",
    ".windsurf/rules/",
    ".windsurf/scripts/",
    ".windsurf/schemas/",
    ".windsurf/state/",
    ".windsurf/templates/",
    ".windsurf/reminders/",
)
BLOCKED_FILES = {
    ".windsurf/hooks.json",
    ".windsurf/mcp_config.json",
    ".windsurf/RULES_INDEX.md",
}
ARCHIVE_EXEMPT_PREFIXES = (
    ".cursor/plans/_archive/",
    ".cursor/windsurf_compat/",
    "docs/archive/windsurf/",
)


def _staged_files() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
            shell=False,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        print(f"[no_active_windsurf] could not inspect staged files: {exc}", file=sys.stderr)
        return []
    if result.returncode != 0:
        print(result.stderr.strip(), file=sys.stderr)
        return []
    return [line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]


def _is_blocked(path: str) -> bool:
    if path.startswith(ARCHIVE_EXEMPT_PREFIXES):
        return False
    if path in BLOCKED_FILES:
        return True
    return path.startswith(BLOCKED_PREFIXES)


def main() -> int:
    if os.environ.get("NO_ACTIVE_WINDSURF_BYPASS") == "1":
        print("[no_active_windsurf] BYPASS=1", file=sys.stderr)
        return 0

    blocked = [path for path in _staged_files() if _is_blocked(path)]
    if not blocked:
        print("[no_active_windsurf] OK: no active .windsurf workflow edits staged")
        return 0

    print("[no_active_windsurf] FAIL: active .windsurf workflow edits are deprecated:", file=sys.stderr)
    for path in blocked:
        print(f"  - {path}", file=sys.stderr)
    print(
        "Move active governance/workflow changes to .cursor/**, or archive historical material "
        "under docs/archive/windsurf/ or .cursor/*_legacy*.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

