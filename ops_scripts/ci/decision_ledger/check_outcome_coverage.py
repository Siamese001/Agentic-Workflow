#!/usr/bin/env python3
"""
check_outcome_coverage.py — CI gate: every surfaced decision older than the
coverage window must have an outcome row bound.

DEFAULT COVERAGE WINDOW
    24 hours — a decision surfaced more than 24h ago without an outcome
    signals a broken learning loop (binder not running, or no commit produced).

EXIT CODES
    0 = all surfaced decisions either young (<24h) or bound
    1 = one or more stale unbound decisions (violations)
    2 = DB unreachable / fatal error

CONSTITUTIONAL
    - No bare except; catches sqlite3.Error, ValueError
    - UTF-8 stdio
    - Bounded query (LIMIT 1000)
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = REPO_ROOT / ".codex" / "state" / "refactor_decisions" / "refactor_decision_ledger.sqlite"
BASELINE_PATH = Path(__file__).resolve().parent / "baselines" / "outcome_coverage_baseline.json"

DEFAULT_WINDOW_HOURS = 24


def _load_baseline() -> tuple[int, int]:
    """Return (baseline_count, window_hours) from JSON, or (0, DEFAULT) on error."""
    if not BASELINE_PATH.exists():
        return 0, DEFAULT_WINDOW_HOURS
    try:
        data = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
        return (
            int(data.get("baseline_stale_unbound", 0)),
            int(data.get("window_hours", DEFAULT_WINDOW_HOURS)),
        )
    except (OSError, ValueError, json.JSONDecodeError):
        return 0, DEFAULT_WINDOW_HOURS


def _parse_iso(ts: str) -> datetime | None:
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="CI gate for decision outcome coverage.")
    baseline_default, window_default = _load_baseline()
    parser.add_argument(
        "--window-hours",
        type=int,
        default=window_default,
        help=f"Coverage window in hours (baseline default {window_default})",
    )
    parser.add_argument(
        "--baseline",
        type=int,
        default=baseline_default,
        help=f"Allowed stale unbound decisions (baseline default {baseline_default})",
    )
    args = parser.parse_args()

    if not DB_PATH.exists():
        # Fresh checkout with no ledger yet = acceptable; CI passes.
        print(f"[check_outcome_coverage] Ledger absent: {DB_PATH} — PASS (fresh state).")
        return 0

    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=10)
        conn.row_factory = sqlite3.Row
    except sqlite3.Error as exc:
        print(f"[check_outcome_coverage] Cannot open ledger: {exc}", file=sys.stderr)
        return 2

    threshold = datetime.now(timezone.utc) - timedelta(hours=args.window_hours)
    try:
        rows = conn.execute(
            """
            SELECT d.decision_id, d.created_at, d.decision_type
              FROM decisions d
              LEFT JOIN decision_outcomes o ON o.decision_id = d.decision_id
             WHERE d.status = 'surfaced'
               AND o.outcome_id IS NULL
             ORDER BY d.created_at ASC
             LIMIT 1000
            """
        ).fetchall()
    except sqlite3.Error as exc:
        print(f"[check_outcome_coverage] Query failed: {exc}", file=sys.stderr)
        conn.close()
        return 2
    conn.close()

    stale = []
    for row in rows:
        ts = _parse_iso(row["created_at"] or "")
        if ts is None:
            continue
        if ts < threshold:
            stale.append((row["decision_id"], row["created_at"], row["decision_type"]))

    if len(stale) <= args.baseline:
        print(
            f"[check_outcome_coverage] PASS — {len(stale)} stale unbound decision(s); "
            f"baseline={args.baseline}, window={args.window_hours}h."
        )
        return 0

    print(
        f"[check_outcome_coverage] FAIL — {len(stale)} stale unbound decision(s) "
        f"exceed baseline={args.baseline} (window={args.window_hours}h):"
    )
    for did, created, dtype in stale[:20]:
        print(f"  - {did}  created={created}  type={dtype}")
    if len(stale) > 20:
        print(f"  … {len(stale) - 20} more")
    print(
        "\nRemediation: run `python .codex/governance/scripts/post_commit_outcome_binder.py` "
        "to bind outcomes from recent commits."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
