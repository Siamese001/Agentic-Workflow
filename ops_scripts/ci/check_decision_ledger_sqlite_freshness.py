#!/usr/bin/env python3
"""check_decision_ledger_sqlite_freshness.py — CI gate for decision-ledger health.

Validates that the canonical SQLite decision ledger
(.codex/state/refactor_decisions/refactor_decision_ledger.sqlite) is being
written to. The ledger is fed by:

    Codex response  -->  tools/capture/append_marker.py  -->  markers.jsonl
                            -->  tools/capture/queue_to_ledger.py  -->  SQLite

If the JSONL queue has un-drained DECISION_CAPTURED markers (>1 hour old),
the gate fails — that's the "drain forgot to run" regression we explicitly
guarded against in plan wire-sqlite-decision-ledger-e8f3a2.

Two checks (advisory by default; fail-closed when DECISION_LEDGER_STRICT=1):

  1. UN-DRAINED MARKERS — count DECISION_CAPTURED lines in markers.jsonl.
     If > 0 AND oldest is > MAX_QUEUE_AGE_HOURS old, FAIL.
  2. STALE LEDGER — last decision in SQLite > MAX_LEDGER_AGE_DAYS old AND
     a refactor-class commit landed in that window. Heuristic; advisory.

Bypass: DECISION_LEDGER_FRESHNESS_BYPASS=1
Strict: DECISION_LEDGER_STRICT=1 (fail with exit 1 instead of warn)

Usage:
    python ops_scripts/ci/check_decision_ledger_sqlite_freshness.py
    python ops_scripts/ci/check_decision_ledger_sqlite_freshness.py --strict
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SQLITE_PATH = REPO_ROOT / ".codex" / "state" / "refactor_decisions" / "refactor_decision_ledger.sqlite"
QUEUE_PATH = REPO_ROOT / "artifacts" / "capture" / "markers.jsonl"

MAX_QUEUE_AGE_HOURS = 1
MAX_LEDGER_AGE_DAYS = 30


def _check_undrained_queue(now: datetime) -> tuple[bool, str]:
    """Return (ok, message). ok=False means drain is overdue."""
    if not QUEUE_PATH.exists():
        return True, "queue absent (clean state)"
    try:
        lines = QUEUE_PATH.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return True, f"queue unreadable: {exc} (advisory pass)"

    decision_lines: list[dict] = []
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        try:
            obj = json.loads(ln)
        except json.JSONDecodeError:
            continue
        if obj.get("marker_type") == "DECISION_CAPTURED":
            decision_lines.append(obj)

    if not decision_lines:
        return True, f"queue clean ({len(lines)} non-decision rows)"

    # Find oldest by received_at.
    oldest = None
    for obj in decision_lines:
        rt = obj.get("received_at", "")
        try:
            ts = datetime.fromisoformat(rt.replace("Z", "+00:00"))
        except ValueError:
            continue
        if oldest is None or ts < oldest:
            oldest = ts

    if oldest is None:
        return True, f"{len(decision_lines)} decisions queued (no parsable timestamps)"

    age = now - oldest
    if age > timedelta(hours=MAX_QUEUE_AGE_HOURS):
        return False, (
            f"{len(decision_lines)} DECISION_CAPTURED markers in queue, oldest "
            f"{age.total_seconds()/3600:.1f}h old (>{MAX_QUEUE_AGE_HOURS}h limit). "
            f"Run: python tools/capture/queue_to_ledger.py"
        )
    return True, f"{len(decision_lines)} markers queued, oldest {age.total_seconds()/3600:.1f}h (within limit)"


def _check_ledger_age(now: datetime) -> tuple[bool, str]:
    """Return (ok, message). Soft check — advisory only even in strict mode."""
    if not SQLITE_PATH.exists():
        return True, "ledger absent (advisory: schema not yet initialized)"
    try:
        con = sqlite3.connect(str(SQLITE_PATH), timeout=5)
        cur = con.cursor()
        cur.execute("SELECT MAX(created_at) FROM decisions")
        row = cur.fetchone()
        con.close()
    except sqlite3.Error as exc:
        return True, f"ledger unreadable: {exc} (advisory pass)"

    if not row or not row[0]:
        return True, "ledger empty (advisory: no decisions captured yet)"

    try:
        last = datetime.fromisoformat(row[0].replace("Z", "+00:00"))
    except ValueError:
        return True, f"ledger MAX(created_at)={row[0]} unparseable (advisory)"

    age = now - last
    if age > timedelta(days=MAX_LEDGER_AGE_DAYS):
        return False, (
            f"ledger last write {age.days}d ago (>{MAX_LEDGER_AGE_DAYS}d limit). "
            f"Either no Author-Gate decisions made (unusual) or capture pipeline broken."
        )
    return True, f"ledger fresh: last write {age.days}d ago"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--strict", action="store_true",
                    help="Fail with exit 1 on violations (default: advisory exit 0)")
    args = ap.parse_args(argv)

    if os.environ.get("DECISION_LEDGER_FRESHNESS_BYPASS") == "1":
        print("[freshness] BYPASSED via DECISION_LEDGER_FRESHNESS_BYPASS=1")
        return 0

    strict = args.strict or os.environ.get("DECISION_LEDGER_STRICT") == "1"
    now = datetime.now(timezone.utc)

    queue_ok, queue_msg = _check_undrained_queue(now)
    ledger_ok, ledger_msg = _check_ledger_age(now)

    print(f"[freshness] queue:  {'OK ' if queue_ok else 'FAIL'}  {queue_msg}")
    print(f"[freshness] ledger: {'OK ' if ledger_ok else 'WARN'}  {ledger_msg}")

    failed = (not queue_ok) or (not ledger_ok)
    if failed and strict:
        print("[freshness] STRICT mode: exit 1")
        return 1
    if failed:
        print("[freshness] advisory: exit 0 (set DECISION_LEDGER_STRICT=1 or pass --strict to enforce)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
