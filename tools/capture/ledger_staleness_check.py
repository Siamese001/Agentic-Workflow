#!/usr/bin/env python3
"""ledger_staleness_check.py — Fail-closed monitor for the Author-Gate ledger.

This is THE gate that would have caught the 2026-04-23 → 2026-04-27 outage
documented in docs/reports/rcas/rca-author-gate-capture-outage-20260427-a7c3b2.md.

Reads the most recent ``created_at`` from the decision ledger; exits 2 (BLOCK)
when the newest row is older than ``--max-age-hours`` (default 24). The exit
code matches the Windsurf pre-hook convention: 2 = block, 0 = allow.

Invocation:
    python tools/capture/ledger_staleness_check.py
    python tools/capture/ledger_staleness_check.py --max-age-hours 48 --advisory
    python tools/capture/ledger_staleness_check.py --json   # structured output

Designed to be wired into:
  - ``pre_user_prompt`` hook (blocks session start if ledger is silent)
  - CI as a daily health check
  - Pre-push safety net

Environment:
  AUTHOR_GATE_STALE_BYPASS=1   — advisory only, never blocks
  AUTHOR_GATE_STALE_THRESHOLD_H — override default threshold in hours

Exit codes:
  0  fresh (newest row within threshold)
  2  stale and strict mode (BLOCK)
  3  ledger missing or unreadable (BLOCK — infrastructure defect)
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

from tools.refactor_decisions.ledger_paths import REFACTOR_DECISION_LEDGER_DB

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LEDGER = REFACTOR_DECISION_LEDGER_DB
DEFAULT_THRESHOLD_H = 24.0

# Actionable guidance emitted with the BLOCK message so the user knows exactly
# what to do.
_REMEDIATION = """
Remediation:
  1. Drain any pending markers:   python tools/capture/queue_to_ledger.py
  2. Re-check ledger age:          python tools/capture/ledger_staleness_check.py
  3. If step 1 yields zero rows:   investigate Windsurf hook health
     - Check:    artifacts/cursor/post_cursor_agent_heartbeat.jsonl (tail)
     - Reference: docs/reports/rcas/rca-author-gate-capture-outage-20260427-a7c3b2.md
  4. Confirm pipeline end-to-end:  python tools/capture/append_marker.py --marker "DECISION_CAPTURED: type=test_strategy, repo_area=diagnostic, selected=manual-probe, outcome=executed, principle=test, precedent=none"
                                   python tools/capture/queue_to_ledger.py
""".strip()


def read_latest_created_at(ledger_path: Path) -> str | None:
    """Return newest created_at ISO string, or None if ledger missing/empty."""
    if not ledger_path.exists():
        return None
    try:
        with sqlite3.connect(f"file:{ledger_path}?mode=ro", uri=True, timeout=5) as con:
            cur = con.execute("SELECT MAX(created_at) FROM decisions")
            row = cur.fetchone()
    except sqlite3.Error:
        return None
    if not row or row[0] is None:
        return None
    return str(row[0])


def parse_iso(ts: str) -> datetime | None:
    """Parse an ISO-8601 timestamp; tolerant of trailing 'Z' and offsets."""
    if not ts:
        return None
    candidate = ts.strip()
    if candidate.endswith("Z"):
        candidate = candidate[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(candidate)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def evaluate(ledger_path: Path, max_age_hours: float) -> dict:
    """Evaluate ledger freshness; returns a structured report.

    Report keys:
      status         "fresh" | "stale" | "ledger_missing" | "ledger_empty"
      max_created_at last row's ISO timestamp or None
      age_hours      computed age in hours or None
      threshold_h    the threshold applied
      ledger_path    absolute path evaluated
    """
    report = {
        "status": "unknown",
        "max_created_at": None,
        "age_hours": None,
        "threshold_h": max_age_hours,
        "ledger_path": str(ledger_path),
    }
    if not ledger_path.exists():
        report["status"] = "ledger_missing"
        return report
    raw = read_latest_created_at(ledger_path)
    if raw is None:
        report["status"] = "ledger_empty"
        return report
    report["max_created_at"] = raw
    dt = parse_iso(raw)
    if dt is None:
        # Unparseable timestamp — treat as stale out of paranoia.
        report["status"] = "stale"
        return report
    age = datetime.now(timezone.utc) - dt
    hours = age.total_seconds() / 3600
    report["age_hours"] = round(hours, 2)
    report["status"] = "fresh" if hours <= max_age_hours else "stale"
    return report


def _format_human(report: dict) -> str:
    status = report["status"]
    mx = report["max_created_at"]
    age = report["age_hours"]
    th = report["threshold_h"]
    if status == "fresh":
        return f"[ledger-staleness] OK: newest row {mx} ({age}h old, threshold {th}h)"
    if status == "stale":
        return (
            f"[ledger-staleness] STALE: newest row {mx} is {age}h old "
            f"(threshold {th}h).\n{_REMEDIATION}"
        )
    if status == "ledger_missing":
        return (
            f"[ledger-staleness] MISSING: {report['ledger_path']} does not exist. "
            f"This is an infrastructure defect.\n{_REMEDIATION}"
        )
    if status == "ledger_empty":
        return (
            f"[ledger-staleness] EMPTY: {report['ledger_path']} exists but has "
            f"no decisions. Cold-start OK on a brand-new repo; treat as stale "
            f"otherwise.\n{_REMEDIATION}"
        )
    return f"[ledger-staleness] UNKNOWN: {report}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    default_h = float(os.environ.get("AUTHOR_GATE_STALE_THRESHOLD_H", DEFAULT_THRESHOLD_H))
    parser.add_argument("--max-age-hours", type=float, default=default_h)
    parser.add_argument("--advisory", action="store_true", help="Report only, do not fail.")
    parser.add_argument("--json", action="store_true", help="Emit report as JSON (single line).")
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress fresh-status success message on stdout (stale still prints).",
    )
    args = parser.parse_args(argv)

    report = evaluate(args.ledger, args.max_age_hours)

    if args.json:
        print(json.dumps(report))
    else:
        msg = _format_human(report)
        if report["status"] == "fresh" and args.quiet:
            pass
        elif report["status"] == "fresh":
            print(msg)
        else:
            print(msg, file=sys.stderr)

    if os.environ.get("AUTHOR_GATE_STALE_BYPASS") == "1":
        return 0
    if args.advisory:
        return 0

    if report["status"] == "fresh":
        return 0
    if report["status"] in ("ledger_missing",):
        return 3
    # stale or ledger_empty → BLOCK (exit 2 matches Windsurf pre-hook convention)
    return 2


if __name__ == "__main__":
    sys.exit(main())
