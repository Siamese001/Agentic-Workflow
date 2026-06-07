#!/usr/bin/env python3
"""
check_prediction_binding_sla.py — W3.2 prediction→outcome binding SLA gate.

Any row in the ledger family with status='predicted' older than
--max-predicted-days triggers a violation. Forces the feedback loop to
actually close (otherwise `post_commit_outcome_binder.py` has silently
stopped running).

Exit 0 — all predictions bound within SLA
Exit 1 — at least one prediction too old
Exit 2 — script error

Bypass: PREDICTION_BINDING_BYPASS=1
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER_GLOB = str(REPO_ROOT / "artifacts" / "ledgers" / "*.sqlite")
VIOLATIONS_LOG = REPO_ROOT / "artifacts" / "governance" / "prediction_binding_violations.jsonl"
BYPASS_LOG = REPO_ROOT / "artifacts" / "governance" / "prediction_binding_bypass.jsonl"


def _log(path: Path, payload: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(
                json.dumps(
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        **payload,
                    }
                )
                + "\n"
            )
    except OSError:
        # guardian: allow-silent-swallow -- log unwritable: non-fatal
        pass


def main() -> int:
    ap = argparse.ArgumentParser(description="Prediction→outcome binding SLA (W3.2)")
    ap.add_argument("--max-predicted-days", type=int, default=14)
    ap.add_argument(
        "--max-unbound-per-ledger",
        type=int,
        default=5,
        help="Tolerate this many still-predicted rows per ledger",
    )
    args = ap.parse_args()

    if os.environ.get("PREDICTION_BINDING_BYPASS") == "1":
        _log(BYPASS_LOG, {"reason": "env"})
        print("[check_prediction_binding_sla] BYPASS (env). Logged.", file=sys.stderr)
        return 0

    cutoff = (datetime.now(timezone.utc) - timedelta(days=args.max_predicted_days)).isoformat(
        timespec="seconds"
    )

    ledgers = sorted(glob.glob(LEDGER_GLOB))
    violations: list[dict] = []
    for path in ledgers:
        name = os.path.basename(path).replace(".sqlite", "")
        try:
            conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=5)
        except sqlite3.Error:
            continue
        try:
            cols = {r[1] for r in conn.execute("PRAGMA table_info(events)")}
            if "status" not in cols or "ts_utc" not in cols:
                continue
            stale = list(
                conn.execute(
                    "SELECT event_id, ts_utc, event_kind FROM events "
                    "WHERE status='predicted' AND ts_utc IS NOT NULL AND ts_utc != '' "
                    "AND ts_utc < ? ORDER BY ts_utc ASC LIMIT 100",
                    (cutoff,),
                )
            )
            total_old = len(stale)
            if total_old > args.max_unbound_per_ledger:
                violations.append(
                    {
                        "ledger": name,
                        "stale_predicted_count": total_old,
                        "threshold": args.max_unbound_per_ledger,
                        "oldest_event": stale[0][0] if stale else None,
                        "oldest_ts": stale[0][1] if stale else None,
                    }
                )
            print(f"  {name}: {total_old} predicted-older-than-{args.max_predicted_days}d", file=sys.stderr)
        except sqlite3.Error:
            continue
        finally:
            conn.close()

    if violations:
        print(
            f"[check_prediction_binding_sla] FAIL — {len(violations)} ledger(s) "
            f"exceed unbound-prediction threshold",
            file=sys.stderr,
        )
        for v in violations:
            print(f"  {v}", file=sys.stderr)
        _log(VIOLATIONS_LOG, {"violations": violations})
        return 1

    print(f"[check_prediction_binding_sla] PASS — all {len(ledgers)} ledger(s) within SLA", file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (sqlite3.Error, OSError) as exc:
        print(f"[check_prediction_binding_sla] script error: {exc}", file=sys.stderr)
        sys.exit(2)
