#!/usr/bin/env python3
"""R5: Staleness audit for exclusion entries.

For every path literal in config/excluded_paths.yaml, check:
    1. Does the path exist on the filesystem today?
    2. Has it ever been committed to git history (any branch)?
    3. When was it last touched in git (days since last commit)?

An entry is *stale candidate* if both filesystem-missing AND git-history-empty —
i.e. it has never existed in the repo. Example: the `06_data` entry removed in R1.

An entry is *dormant* if missing from FS but present in history longer ago than
--dormant-days (default 180). These are usually safe to remove but worth human
review because they may be waiting for a future directory.

Usage:
    python tools/maintenance/audit_exclusion_staleness.py
    python tools/maintenance/audit_exclusion_staleness.py --json
    python tools/maintenance/audit_exclusion_staleness.py --dormant-days 365
    python tools/maintenance/audit_exclusion_staleness.py --category data_dirs

Not a CI gate — run on cadence (quarterly) as a human-reviewed report.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
YAML_PATH = REPO_ROOT / "config" / "excluded_paths.yaml"

# Categories whose entries are interpreted as filesystem paths (vs regex patterns).
# `precommit_excludes` and `file_patterns` are regex/glob and are not audited here.
PATH_CATEGORIES: tuple[str, ...] = (
    "build_cache_dirs",
    "version_control_dirs",
    "virtual_env_dirs",
    "coverage_dirs",
    "archive_dirs",
    "ide_dirs",
    "vendor_dirs",
    "data_dirs",
    "special_dirs",
    "windsurf_state_dirs",
    "sovereign_excluded_folders",
    "global_excluded_dirs",
    "discovery_excluded_territories",
    "codeium_patterns",
)

# Defensive categories: entries here are expected to NEVER exist in repo (that's
# the whole point of excluding them). "Never committed" is success, not staleness.
# Retrospective categories are the inverse — they were added because a specific
# path existed, and they become candidates for removal when that path is gone.
DEFENSIVE_CATEGORIES: frozenset[str] = frozenset(
    {
        "build_cache_dirs",
        "version_control_dirs",
        "virtual_env_dirs",
        "coverage_dirs",
        "ide_dirs",
        "vendor_dirs",
        "special_dirs",
        "windsurf_state_dirs",
        "sovereign_excluded_folders",
        "global_excluded_dirs",
        "discovery_excluded_territories",
    },
)

# Some entries are glob patterns, not real paths. Skip them from FS checks.
_GLOB_TOKENS = re.compile(r"[\*\?\[\]]")


def _is_glob(entry: str) -> bool:
    return bool(_GLOB_TOKENS.search(entry))


def _load_yaml() -> dict:
    import yaml

    with YAML_PATH.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        return {}
    return data


def _git_log_days(path: str) -> int | None:
    """Return days since most recent commit touching `path` across all refs.

    None means the path has zero commits (never committed).
    """
    try:
        out = subprocess.run(
            ["git", "log", "--all", "-1", "--format=%cI", "--", path],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError):
        return None
    line = (out.stdout or "").strip()
    if not line:
        return None
    try:
        commit_time = datetime.fromisoformat(line)
    except ValueError:
        return None
    now = datetime.now(timezone.utc)
    if commit_time.tzinfo is None:
        commit_time = commit_time.replace(tzinfo=timezone.utc)
    return int((now - commit_time).total_seconds() // 86400)


def _classify(category: str, entry: str, dormant_days: int) -> tuple[str, dict]:
    """Return (status, detail) for a single entry.

    Status is one of:
        "glob"       — skipped (pattern, not literal path)
        "defensive"  — never-committed entry in a category that's defensive by
                       design (e.g. .venv in virtual_env_dirs — its absence is
                       the success criterion, not a problem)
        "live"       — exists on disk today
        "dormant"    — missing from disk, last commit older than dormant_days
        "recent"     — missing from disk, committed within dormant_days
        "dead"       — missing from disk AND never committed AND category is
                       retrospective (a specific path, not a defensive prophylactic)
    """
    if _is_glob(entry):
        return "glob", {"reason": "pattern entry — not a literal path"}
    fs_path = REPO_ROOT / entry
    exists = fs_path.exists()
    if exists:
        return "live", {"fs_exists": True}
    days = _git_log_days(entry)
    if days is None:
        if category in DEFENSIVE_CATEGORIES:
            return "defensive", {
                "fs_exists": False,
                "git_commits": 0,
                "reason": "defensive-by-design category",
            }
        return "dead", {"fs_exists": False, "git_commits": 0}
    if days >= dormant_days:
        return "dormant", {"fs_exists": False, "days_since_commit": days}
    return "recent", {"fs_exists": False, "days_since_commit": days}


def _iter_entries(yaml_data: dict, categories: Iterable[str]) -> Iterable[tuple[str, str]]:
    for category in categories:
        entries = yaml_data.get(category)
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if isinstance(entry, str):
                yield category, entry


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit exclusion staleness.")
    parser.add_argument(
        "--dormant-days",
        type=int,
        default=180,
        help="Entries missing from disk with no commit in N days become dormant (default 180).",
    )
    parser.add_argument(
        "--category",
        action="append",
        default=[],
        help="Restrict audit to specific YAML categories (repeatable).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of a human report.",
    )
    parser.add_argument(
        "--fail-on-dead",
        action="store_true",
        help="Exit 1 if any dead entries remain (for periodic CI reminders).",
    )
    args = parser.parse_args()

    yaml_data = _load_yaml()
    categories = args.category or PATH_CATEGORIES

    buckets: dict[str, list[dict]] = {
        "dead": [],
        "dormant": [],
        "recent": [],
        "live": [],
        "defensive": [],
        "glob": [],
    }

    for category, entry in _iter_entries(yaml_data, categories):
        status, detail = _classify(category, entry, args.dormant_days)
        buckets[status].append({"category": category, "entry": entry, **detail})

    if args.json:
        report = {
            "yaml": str(YAML_PATH.relative_to(REPO_ROOT).as_posix()),
            "dormant_threshold_days": args.dormant_days,
            "counts": {k: len(v) for k, v in buckets.items()},
            "dead": buckets["dead"],
            "dormant": buckets["dormant"],
            "recent": buckets["recent"],
        }
        print(json.dumps(report, indent=2))
    else:
        total = sum(len(v) for v in buckets.values())
        print(f"Exclusion staleness audit — {YAML_PATH.as_posix()}")
        print(f"Total audited: {total}")
        print(f"  live:      {len(buckets['live'])}   (exists on disk today)")
        print(
            f"  recent:    {len(buckets['recent'])}   (missing from disk, committed within {args.dormant_days}d)"
        )
        print(
            f"  dormant:   {len(buckets['dormant'])}   (missing from disk, last commit >={args.dormant_days}d ago)"
        )
        print(
            f"  dead:      {len(buckets['dead'])}   (retrospective category, missing, NEVER committed — REMOVE)"
        )
        print(f"  defensive: {len(buckets['defensive'])}   (defensive-by-design, never-committed is success)")
        print(f"  glob:      {len(buckets['glob'])}   (pattern entries, FS audit skipped)")
        if buckets["dead"]:
            print("\nDead entries (NEVER committed):")
            for item in buckets["dead"]:
                print(f"  - [{item['category']}]  {item['entry']}")
        if buckets["dormant"]:
            print(f"\nDormant entries (>={args.dormant_days}d since last commit):")
            for item in sorted(buckets["dormant"], key=lambda x: -x.get("days_since_commit", 0)):
                d = item.get("days_since_commit", "?")
                print(f"  - [{item['category']}]  {item['entry']}   ({d}d)")

    if args.fail_on_dead and buckets["dead"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
