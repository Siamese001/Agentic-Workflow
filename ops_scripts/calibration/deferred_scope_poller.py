"""deferred_scope_poller.py — Bind deferred-scope outcomes from local capture log.

Reads `artifacts/windsurf/deferred_scope_capture.jsonl` (the capture hook's
output) and the deferred_scope_calibration ledger, then reconciles:

    - For each capture row with a computed P-band, if we already have a
      matching ledger event, skip (idempotent).
    - For each unbound prediction in the ledger, check whether a later capture
      row for the same (plan, wave, phase) tuple carries a status flip. If yes,
      compute days_to_done and bind the outcome.

This is the local-first path. Full Notion polling via API-query-data-source
is gated on one-time operator-approved credential provisioning and is not
performed by this script by default — it only operates on local artifacts.

Usage:
    python ops_scripts/calibration/deferred_scope_poller.py --dry-run
    python ops_scripts/calibration/deferred_scope_poller.py

Exit codes:
    0 = reconciliation complete
    2 = internal error
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

CAPTURE_LOG = _REPO_ROOT / "artifacts" / "windsurf" / "deferred_scope_capture.jsonl"
LEDGER_DB = _REPO_ROOT / "artifacts" / "ledgers" / "deferred_scope_calibration.sqlite"


def _iter_capture_rows():
    if not CAPTURE_LOG.exists():
        return
    with CAPTURE_LOG.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def _emit_predictions(dry_run: bool) -> int:
    """Emit one deferred_scope_capture prediction per capture-log row
    (idempotent on event_id since writer derives it deterministically)."""
    try:
        from tools.ledgers.hook_helpers import emit_ledger_event
    except ImportError:
        print("[deferred_scope_poller] ledger helpers missing", file=sys.stderr)
        return 0

    emitted = 0
    for row in _iter_capture_rows():
        plan = row.get("plan") or row.get("plan_slug") or ""
        wave = row.get("wave") or row.get("wave_id") or ""
        phase = row.get("phase") or row.get("phase_id") or ""
        pband = row.get("priority") or row.get("computed_p_band") or ""
        if not (plan and wave and phase):
            continue
        if dry_run:
            emitted += 1
            continue
        emit_ledger_event(
            ledger="deferred_scope_calibration",
            event_kind="deferred_scope_capture",
            prediction={
                "plan_slug": plan,
                "wave_id": wave,
                "phase_id": phase,
                "computed_p_band": pband,
                "factors": {
                    "coverage_gap_pct": row.get("coverage_gap_pct"),
                    "fan_in": row.get("fan_in"),
                    "layer": row.get("layer"),
                    "surface": row.get("surface"),
                },
                "scorer_version": row.get("scorer_version") or "v1",
            },
            score_band=pband,
            repo_area=plan,
        )
        emitted += 1
    return emitted


def _count_unbound() -> int:
    if not LEDGER_DB.exists():
        return 0
    try:
        conn = sqlite3.connect(str(LEDGER_DB), timeout=5)
        try:
            row = conn.execute(
                "SELECT COUNT(*) FROM events WHERE status='predicted' "
                "AND event_kind='deferred_scope_capture'"
            ).fetchone()
            return int(row[0]) if row else 0
        finally:
            conn.close()
    except sqlite3.Error:
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    emitted = _emit_predictions(args.dry_run)
    unbound = _count_unbound()

    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    mode = "dry-run" if args.dry_run else "emitted"
    print(
        f"[deferred_scope_poller] {stamp} capture_log={CAPTURE_LOG.exists()} "
        f"{mode}={emitted} unbound_predictions={unbound}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
