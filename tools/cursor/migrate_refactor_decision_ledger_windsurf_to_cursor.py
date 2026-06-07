#!/usr/bin/env python3
"""migrate_refactor_decision_ledger_windsurf_to_cursor.py — one-shot ledger alignment.

Backs up the Cursor ledger if present, then either copies (empty Cursor) or
merges rows from ``.claude/state/.../refactor_decision_ledger.sqlite`` that
are missing in ``.claude/state/...`` (ATTACH-based INSERT OR IGNORE).

Usage:
    python tools/cursor/migrate_refactor_decision_ledger_windsurf_to_cursor.py
    python tools/cursor/migrate_refactor_decision_ledger_windsurf_to_cursor.py --dry-run

No deletes. Existing Cursor rows are never overwritten.
"""

from __future__ import annotations

import argparse
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CURSOR_DB = REPO_ROOT / ".claude" / "state" / "refactor_decisions" / "refactor_decision_ledger.sqlite"
WINDSURF_DB = REPO_ROOT / ".claude" / "state" / "refactor_decisions" / "refactor_decision_ledger.sqlite"


def _count(conn: sqlite3.Connection, table: str) -> int:
    row = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
    return int(row[0]) if row else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not WINDSURF_DB.is_file():
        print("[migrate] no Windsurf ledger — nothing to migrate", file=sys.stderr)
        return 0

    CURSOR_DB.parent.mkdir(parents=True, exist_ok=True)

    cursor_exists = CURSOR_DB.is_file()
    cursor_count = 0
    if cursor_exists:
        c = sqlite3.connect(str(CURSOR_DB))
        try:
            cursor_count = _count(c, "decisions")
        except sqlite3.Error:
            cursor_count = 0
        finally:
            c.close()

    w = sqlite3.connect(str(WINDSURF_DB))
    try:
        windsurf_count = _count(w, "decisions")
    finally:
        w.close()

    print(f"[migrate] cursor_decisions={cursor_count} windsurf_decisions={windsurf_count} dry_run={args.dry_run}")

    if cursor_count == 0 and windsurf_count > 0:
        if args.dry_run:
            print("[migrate] would copy Windsurf → Cursor (Cursor empty)")
            return 0
        if cursor_exists:
            bak = CURSOR_DB.with_suffix(
                CURSOR_DB.suffix + ".bak." + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            )
            shutil.copy2(CURSOR_DB, bak)
            print(f"[migrate] backed up existing Cursor DB → {bak.relative_to(REPO_ROOT)}")
        shutil.copy2(WINDSURF_DB, CURSOR_DB)
        print("[migrate] copied Windsurf ledger → Cursor path")
        return 0

    if windsurf_count == 0:
        print("[migrate] Windsurf ledger empty — no merge")
        return 0

    if args.dry_run:
        print("[migrate] would merge any missing decision_id rows from Windsurf into Cursor")
        return 0

    if cursor_exists and cursor_count > 0:
        bak = CURSOR_DB.with_suffix(
            CURSOR_DB.suffix + ".bak." + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        )
        shutil.copy2(CURSOR_DB, bak)
        print(f"[migrate] backup → {bak.relative_to(REPO_ROOT)}")

    aux = str(WINDSURF_DB.resolve()).replace("\\", "/").replace("'", "''")
    conn = sqlite3.connect(str(CURSOR_DB), timeout=30)
    try:
        conn.execute(f"ATTACH DATABASE '{aux}' AS aux")
        for tbl in ("decision_scope", "decision_outcomes", "decision_signals"):
            try:
                conn.execute(f"INSERT OR IGNORE INTO {tbl} SELECT * FROM aux.{tbl}")
            except sqlite3.Error as exc:
                print(f"[migrate] WARN merge {tbl}: {exc}", file=sys.stderr)
        try:
            conn.execute("INSERT OR IGNORE INTO decisions SELECT * FROM aux.decisions")
        except sqlite3.Error as exc:
            print(f"[migrate] ERROR merge decisions: {exc}", file=sys.stderr)
            return 1
        try:
            conn.execute(
                "INSERT OR IGNORE INTO decisions_fts(rowid, decision_id, normalized_intent, "
                "request_summary, user_goal, selection_rationale) "
                "SELECT rowid, decision_id, normalized_intent, request_summary, user_goal, selection_rationale "
                "FROM aux.decisions_fts"
            )
        except sqlite3.Error:
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO decisions_fts(decision_id, normalized_intent, request_summary, "
                    "user_goal, selection_rationale) "
                    "SELECT decision_id, normalized_intent, request_summary, user_goal, selection_rationale "
                    "FROM aux.decisions_fts"
                )
            except sqlite3.Error as exc:
                print(f"[migrate] WARN decisions_fts merge: {exc}", file=sys.stderr)
        conn.commit()
        print("[migrate] merge complete")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
