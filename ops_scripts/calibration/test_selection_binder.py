"""test_selection_binder.py — Bind pytest actual-pass/fail to triage_selection rows.

Reads .pytest_cache/v/cache/lastfailed (the set of tests that failed most
recent pytest run) and binds outcome rows on every unbound triage_selection
prediction in the test_selection ledger.

This is a conservative binder: it can confirm whether selected_paths caught
the failing tests (precision) but cannot alone measure recall without a
full-suite reference run. For now it records:

    confirmed_failures   — tests in selected_paths that are now in lastfailed
    missed_failures      — tests in lastfailed not covered by selected_paths
    selection_accuracy   — confirmed / max(1, total_failures)

score_band:
    perfect   — no lastfailed OR confirmed == total (all caught)
    partial   — at least one confirmed, at least one missed
    miss      — lastfailed nonempty AND confirmed == 0

Usage:
    python ops_scripts/calibration/test_selection_binder.py
    python ops_scripts/calibration/test_selection_binder.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

LEDGER_DB = _REPO_ROOT / "artifacts" / "ledgers" / "test_selection.sqlite"
LASTFAILED = _REPO_ROOT / ".pytest_cache" / "v" / "cache" / "lastfailed"


def _load_lastfailed() -> set[str]:
    """Return set of failing test IDs (e.g. 'tests/foo.py::test_bar')."""
    if not LASTFAILED.exists():
        return set()
    try:
        data = json.loads(LASTFAILED.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    if isinstance(data, dict):
        # pytest stores {nodeid: True}
        return {k for k, v in data.items() if v}
    return set()


def _unbound_predictions(conn: sqlite3.Connection, limit: int) -> list[dict]:
    rows = conn.execute(
        """
        SELECT event_id, ts_utc, prediction_json
          FROM events
         WHERE event_kind = 'triage_selection'
           AND status = 'predicted'
         ORDER BY ts_utc ASC
         LIMIT ?
        """,
        (limit,),
    ).fetchall()
    result: list[dict] = []
    for eid, ts_utc, pred_json in rows:
        try:
            pred = json.loads(pred_json) if pred_json else {}
        except json.JSONDecodeError:
            pred = {}
        result.append({"event_id": eid, "ts_utc": ts_utc, "prediction": pred})
    return result


def _covers(selected_paths: list[str], failing_id: str) -> bool:
    """Is the failing pytest nodeid covered by any selected path prefix?"""
    if not selected_paths:
        return True  # full-suite selection covers everything
    file_part = failing_id.split("::", 1)[0]
    for sel in selected_paths:
        if "::" in sel:
            # exact test id selection
            if failing_id == sel or failing_id.startswith(sel + "["):
                return True
        else:
            # file-path selection — match if failing file is under it
            if file_part == sel or file_part.startswith(sel.rstrip("/") + "/"):
                return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lookback", type=int, default=100)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not LEDGER_DB.exists():
        print(f"[test_selection_binder] ledger not found: {LEDGER_DB}", file=sys.stderr)
        return 0

    try:
        from tools.ledgers.hook_helpers import bind_ledger_outcome
    except ImportError:
        print("[test_selection_binder] ledger helpers missing", file=sys.stderr)
        return 2

    lastfailed = _load_lastfailed()
    conn = sqlite3.connect(str(LEDGER_DB), timeout=5)
    try:
        predictions = _unbound_predictions(conn, args.lookback)
    finally:
        conn.close()

    if not predictions:
        print("[test_selection_binder] no unbound triage_selection rows.", file=sys.stderr)
        return 0

    bound = 0
    for pred in predictions:
        selected_paths: list[str] = pred["prediction"].get("selected_paths") or []
        total_failures = len(lastfailed)
        confirmed = [f for f in lastfailed if _covers(selected_paths, f)]
        missed = [f for f in lastfailed if not _covers(selected_paths, f)]
        accuracy = len(confirmed) / max(1, total_failures) if total_failures else 1.0

        if total_failures == 0:
            band = "perfect"
        elif confirmed and not missed:
            band = "perfect"
        elif confirmed:
            band = "partial"
        else:
            band = "miss"

        if args.dry_run:
            bound += 1
            continue

        ok = bind_ledger_outcome(
            ledger="test_selection",
            event_id=pred["event_id"],
            outcome={
                "total_failures": total_failures,
                "confirmed_failures_count": len(confirmed),
                "missed_failures_count": len(missed),
                "confirmed_failures": confirmed[:20],  # cap payload size
                "missed_failures": missed[:20],
                "selection_accuracy": accuracy,
                "source": "pytest_cache_lastfailed",
            },
            score_band=band,
            score_numeric=accuracy,
        )
        if ok:
            bound += 1

    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    mode = "would bind" if args.dry_run else "bound"
    print(
        f"[test_selection_binder] {stamp} {mode}={bound} "
        f"lastfailed_count={len(lastfailed)} scanned_predictions={len(predictions)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
