#!/usr/bin/env python3
"""
audit_promoted_patterns.py — W3.3 sample decision rows with promote_to_pattern=1.

Advisory by default: writes JSON report under artifacts/windsurf/.
Set PROMOTION_AUDIT_FAIL_CLOSED=1 to exit 1 when any sampled row fails hygiene
(high bind confidence, not disputed, clean regression flags).

Constitutional: UTF-8, sqlite3.Error only in DB ops.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.refactor_decisions.ledger_paths import REFACTOR_DECISION_LEDGER_DB  # noqa: E402

ARTIFACT_DIR = REPO_ROOT / "artifacts" / "windsurf"


def _audit_row(row: sqlite3.Row) -> dict:
    bind = (row["bind_confidence"] or "").lower()
    disputed = bool(row["bind_disputed"])
    regress = bool(row["regression_found"])
    rollback = bool(row["rollback_required"])
    ok = bind == "high" and not disputed and not regress and not rollback
    return {
        "decision_id": row["decision_id"],
        "outcome_id": row["outcome_id"],
        "bind_confidence": row["bind_confidence"],
        "bind_disputed": disputed,
        "regression_found": regress,
        "rollback_required": rollback,
        "hygiene_ok": ok,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="W3.3 audit sample for promote_to_pattern rows.")
    parser.add_argument("--sample-size", type=int, default=15, help="Max rows to sample")
    parser.add_argument("--seed", type=int, default=None, help="RNG seed (reproducible samples)")
    args = parser.parse_args()

    fail_closed = os.environ.get("PROMOTION_AUDIT_FAIL_CLOSED", "").strip() in ("1", "true", "yes")
    db_path = REFACTOR_DECISION_LEDGER_DB
    if not db_path.exists():
        print(f"[promotion_audit] SKIP — no ledger at {db_path}", file=sys.stderr)
        return 0

    if args.seed is not None:
        random.seed(args.seed)

    conn: sqlite3.Connection | None = None
    try:
        conn = sqlite3.connect(str(db_path), timeout=10)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT o.outcome_id, o.decision_id, o.bind_confidence, o.bind_disputed,
                   o.regression_found, o.rollback_required
              FROM decision_outcomes o
             WHERE COALESCE(o.promote_to_pattern, 0) = 1
            """
        ).fetchall()
    except sqlite3.Error as exc:
        print(f"[promotion_audit] ERROR: {exc}", file=sys.stderr)
        return 2
    finally:
        if conn is not None:
            conn.close()

    n = min(max(1, args.sample_size), len(rows)) if rows else 0
    sample = random.sample(list(rows), n) if n else []
    details = [_audit_row(r) for r in sample]
    bad = [d for d in details if not d["hygiene_ok"]]

    report = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "ledger": str(db_path),
        "promoted_total": len(rows),
        "sample_size": len(details),
        "hygiene_failures": len(bad),
        "samples": details,
    }

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = ARTIFACT_DIR / "promotion_audit_sample_latest.json"
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    print(f"[promotion_audit] wrote {out_path} failures={len(bad)}/{len(details)}", file=sys.stderr)

    if fail_closed and bad:
        print(
            "[promotion_audit] FAIL — PROMOTION_AUDIT_FAIL_CLOSED=1 and hygiene failures present",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
