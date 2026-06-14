#!/usr/bin/env python3
"""
check_writer_allowlist.py — W5.5 ledger writer-process allowlist.

Validates that the refactor_decision_ledger has an allowlist registered
for which scripts may write rows. Today the ledger has no `writer_script`
column; this gate installs it (schema migration) AND enforces allowlist
via CI: every non-NULL `writer_script` value in recent rows must match
the configured allowlist.

Allowlist (authoritative):
    - post_agent_author_gate_capture.py
    - capture_author_gate.py
    - backfill_cat4_decisions.py
    - promote_author_gate_patterns.py
    - author_gate_ledger_integrity.py

Exit 0 — all recent writers on allowlist (or column absent, schema TBD)
Exit 1 — non-allowlisted writer detected
Exit 2 — script error

Bypass: WRITER_ALLOWLIST_BYPASS=1
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
VIOLATIONS_LOG = REPO_ROOT / "artifacts" / "governance" / "writer_allowlist_violations.jsonl"
BYPASS_LOG = REPO_ROOT / "artifacts" / "governance" / "writer_allowlist_bypass.jsonl"

ALLOWLIST = frozenset(
    {
        # post_agent_author_gate_capture / capture_author_gate / promote_author_gate_patterns
        # retired + archived (Author-Gate teardown, ADR-093); removed as authorised writers.
        "backfill_cat4_decisions.py",
        "author_gate_ledger_integrity.py",
        # add new authorised writers here only
    }
)


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


def _ensure_column(conn: sqlite3.Connection) -> bool:
    try:
        cols = {r[1] for r in conn.execute("PRAGMA table_info(decisions)")}
        if "writer_script" not in cols:
            conn.execute("ALTER TABLE decisions ADD COLUMN writer_script TEXT")
            conn.commit()
            return True  # newly added, no historical data to check
    except sqlite3.Error:
        return False
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description="Writer allowlist (W5.5)")
    ap.add_argument("--window-days", type=int, default=30)
    ap.add_argument("--migrate", action="store_true", help="Add writer_script column if missing")
    args = ap.parse_args()

    if os.environ.get("WRITER_ALLOWLIST_BYPASS") == "1":
        _log(BYPASS_LOG, {"reason": "env"})
        print("[check_writer_allowlist] BYPASS (env). Logged.", file=sys.stderr)
        return 0

    if not LEDGER_DB.exists():
        print("[check_writer_allowlist] OK — ledger not present", file=sys.stderr)
        return 0

    try:
        conn = sqlite3.connect(str(LEDGER_DB), timeout=10)
    except sqlite3.Error as exc:
        print(f"[check_writer_allowlist] script error: {exc}", file=sys.stderr)
        return 2

    try:
        cols = {r[1] for r in conn.execute("PRAGMA table_info(decisions)")}
        if "writer_script" not in cols:
            if args.migrate:
                _ensure_column(conn)
                print("[check_writer_allowlist] MIGRATED — added writer_script column", file=sys.stderr)
                return 0
            print(
                "[check_writer_allowlist] OK — writer_script column not present; "
                "run with --migrate to install (gate is forward-compat)",
                file=sys.stderr,
            )
            return 0

        cutoff = (datetime.now(timezone.utc) - timedelta(days=args.window_days)).isoformat(timespec="seconds")
        rows = list(
            conn.execute(
                "SELECT decision_id, writer_script FROM decisions "
                "WHERE created_at >= ? AND writer_script IS NOT NULL "
                "AND writer_script != ''",
                (cutoff,),
            )
        )
    finally:
        conn.close()

    violations = [{"decision_id": r[0], "writer_script": r[1]} for r in rows if r[1] not in ALLOWLIST]

    print(
        f"[check_writer_allowlist] window={args.window_days}d "
        f"total_with_writer={len(rows)} violations={len(violations)}",
        file=sys.stderr,
    )

    if violations:
        for v in violations[:10]:
            print(f"  VIOLATION {v['decision_id']}: writer={v['writer_script']}", file=sys.stderr)
        _log(VIOLATIONS_LOG, {"violations": violations[:50]})
        return 1

    print("[check_writer_allowlist] PASS", file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (sqlite3.Error, OSError) as exc:
        print(f"[check_writer_allowlist] script error: {exc}", file=sys.stderr)
        sys.exit(2)
