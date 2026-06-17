#!/usr/bin/env python3
"""
check_ag_queue_drain_freshness.py — Weekly drift detection for AG queue drain.

Scans `artifacts/governance/ag_queue_drain_violations.jsonl` for rows in the
last 7 days. Fails (exit 1) when ≥3 non-bypass violations occur within
the window — signals Codex is regressing on the §35 drain discipline.

CLI::

    python ops_scripts/ci/check_ag_queue_drain_freshness.py
    python ops_scripts/ci/check_ag_queue_drain_freshness.py --window-days 14 --threshold 5

Bypass: AG_QUEUE_DRAIN_FRESHNESS_BYPASS=1.

Constitutional tie-in: §35.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VIOLATION_LOG = REPO_ROOT / "artifacts" / "governance" / "ag_queue_drain_violations.jsonl"


def _parse_ts(s: str) -> datetime | None:
    if not s or not isinstance(s, str):
        return None
    try:
        # Accept both "Z" suffix and "+00:00"
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def _load_rows() -> list[dict]:
    if not VIOLATION_LOG.exists():
        return []
    rows: list[dict] = []
    try:
        with VIOLATION_LOG.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(row, dict):
                    rows.append(row)
    except OSError:
        return []
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--window-days", type=int, default=7)
    parser.add_argument("--threshold", type=int, default=3,
                        help="Fail when violations in window reach this count")
    args = parser.parse_args()

    if os.environ.get("AG_QUEUE_DRAIN_FRESHNESS_BYPASS") == "1":
        print("[ag_queue_drain_freshness] BYPASS active — skipping.", file=sys.stderr)
        return 0

    rows = _load_rows()
    if not rows:
        print("[ag_queue_drain_freshness] OK — no violations logged.")
        return 0

    cutoff = datetime.now(timezone.utc) - timedelta(days=args.window_days)
    recent_non_bypass: list[dict] = []
    for r in rows:
        ts = _parse_ts(r.get("timestamp", ""))
        if ts is None or ts < cutoff:
            continue
        if r.get("reason") == "bypass":
            continue
        recent_non_bypass.append(r)

    count = len(recent_non_bypass)
    print(
        f"[ag_queue_drain_freshness] {count} non-bypass violations in last "
        f"{args.window_days} days (threshold {args.threshold})"
    )
    if count >= args.threshold:
        print(
            f"[ag_queue_drain_freshness] FAIL — drift detected. Review "
            f"{VIOLATION_LOG.relative_to(REPO_ROOT)} and reinforce §35 discipline.",
            file=sys.stderr,
        )
        # Show last 3 offending rows
        for r in recent_non_bypass[-3:]:
            print(
                f"  {r.get('timestamp')} plans={r.get('pending_plans')} "
                f"markers={r.get('completion_markers')}",
                file=sys.stderr,
            )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
