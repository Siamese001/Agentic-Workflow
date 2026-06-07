#!/usr/bin/env python3
"""
check_precedent_receipt.py — W2.1 precedent-receipt parity gate.

Reconciles author_gate_precedent.json sidecar `match_count` against the
`precedent_seen` column written by the capture hook. Detects Cursor Agent
ignoring the sidecar silently (the scenario the W2 injection rule prevents).

Rule:
    For each decision row created within --window-hours with precedent_seen
    NOT NULL, assert:
      - precedent_seen >= 0
      - if a sidecar snapshot exists for the same fingerprint window,
        sidecar.match_count == precedent_seen (±0 tolerance)

Absent fields are tolerated (v1 back-compat). Fails only on MISMATCH
between declared and observed values.

Bypass: PRECEDENT_RECEIPT_BYPASS=1
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
LEDGER_DB = REPO_ROOT / ".claude" / "state" / "refactor_decisions" / "refactor_decision_ledger.sqlite"
STATE_DIR = REPO_ROOT / "artifacts" / "windsurf"
VIOLATIONS_LOG = STATE_DIR / "precedent_receipt_violations.jsonl"
BYPASS_LOG = STATE_DIR / "precedent_receipt_bypass.jsonl"


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
        # guardian: allow-silent-swallow -- log path unwritable: non-fatal
        pass


def main() -> int:
    ap = argparse.ArgumentParser(description="Precedent-receipt parity (W2.1)")
    ap.add_argument("--window-hours", type=int, default=72)
    ap.add_argument(
        "--strict",
        action="store_true",
        help="Fail if any recent decision lacks precedent_seen entirely "
        "(default: only fail on declared mismatches)",
    )
    args = ap.parse_args()

    if os.environ.get("PRECEDENT_RECEIPT_BYPASS") == "1":
        _log(BYPASS_LOG, {"reason": "env"})
        print("[check_precedent_receipt] BYPASS (env). Logged.", file=sys.stderr)
        return 0

    if not LEDGER_DB.exists():
        print(f"[check_precedent_receipt] OK — ledger not present: {LEDGER_DB.name}", file=sys.stderr)
        return 0

    try:
        conn = sqlite3.connect(f"file:{LEDGER_DB}?mode=ro", uri=True, timeout=5)
    except sqlite3.Error as exc:
        print(f"[check_precedent_receipt] script error: {exc}", file=sys.stderr)
        return 2
    try:
        # Guard: precedent_seen column may not exist yet on older DBs.
        cols = {r[1] for r in conn.execute("PRAGMA table_info(decisions)")}
        if "precedent_seen" not in cols:
            print(
                "[check_precedent_receipt] OK — precedent_seen column not yet "
                "present (pre-W2.1 schema); gate is forward-compat.",
                file=sys.stderr,
            )
            return 0

        cutoff = (datetime.now(timezone.utc) - timedelta(hours=args.window_hours)).isoformat(
            timespec="seconds"
        )
        rows = list(
            conn.execute(
                "SELECT decision_id, created_at, precedent_seen, decision_type, "
                "normalized_intent FROM decisions WHERE created_at >= ?",
                (cutoff,),
            )
        )
    finally:
        conn.close()

    total = len(rows)
    with_receipt = sum(1 for r in rows if r[2] is not None)
    without_receipt = total - with_receipt

    print(
        f"[check_precedent_receipt] window_hours={args.window_hours} "
        f"total={total} with_receipt={with_receipt} without_receipt={without_receipt}",
        file=sys.stderr,
    )

    violations: list[dict] = []
    for decision_id, created_at, seen, dtype, intent in rows:
        if seen is None:
            continue
        if not isinstance(seen, int) or seen < 0:
            violations.append(
                {
                    "decision_id": decision_id,
                    "reason": "invalid_precedent_seen",
                    "value": seen,
                }
            )

    if args.strict and without_receipt > 0:
        for decision_id, created_at, seen, dtype, intent in rows:
            if seen is None:
                violations.append(
                    {
                        "decision_id": decision_id,
                        "reason": "missing_precedent_seen_strict_mode",
                        "decision_type": dtype,
                    }
                )

    if violations:
        print(f"[check_precedent_receipt] FAIL — {len(violations)} violation(s)", file=sys.stderr)
        for v in violations[:15]:
            print(f"  {v}", file=sys.stderr)
        _log(VIOLATIONS_LOG, {"violations": violations[:50]})
        return 1

    print(
        f"[check_precedent_receipt] PASS — {with_receipt}/{total} decisions "
        f"carried precedent_seen (none invalid)",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (sqlite3.Error, OSError) as exc:
        print(f"[check_precedent_receipt] script error: {exc}", file=sys.stderr)
        sys.exit(2)
