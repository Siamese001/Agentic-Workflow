#!/usr/bin/env python3
"""
check_notion_decision_parity.py — NP16 Author-Gate decision signals (advisory).

Historical behavior compared SQLite ``refactor_decision_ledger.sqlite`` to Notion
Author-Gate Decision Ledger writes mirrored in ``notion_tool_audit.jsonl``.

As of 2026-05-02 the Author-Gate Decision Ledger Notion database is **archived**;
the filesystem ledger under ``.claude/state/refactor_decisions/`` is SSOT
(see AGENTS.md). This gate therefore:

- Counts decisions in the SQLite ledger (rolling window) for telemetry only.
- Treats successful Notion ``API-post-page`` hits to the archived ledger DB as
  **unexpected legacy traffic** when ``NOTION_DECISION_PARITY_FAIL_CLOSED=1``.
- Does **not** fail on SQLite vs Notion count drift (that comparison is retired).

Exit 0 — advisory pass (or bypass)
Exit 1 — fail-closed: legacy Notion Author-Gate posts detected in window
Exit 2 — script error

Bypass: NOTION_DECISION_PARITY_BYPASS=1
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
LEDGER_CURSOR = REPO_ROOT / ".claude" / "state" / "refactor_decisions" / "refactor_decision_ledger.sqlite"
LEDGER_WINDSURF = REPO_ROOT / ".claude" / "state" / "refactor_decisions" / "refactor_decision_ledger.sqlite"
NOTION_AUDIT_PATHS = (
    REPO_ROOT / "artifacts" / "governance" / "notion_tool_audit.jsonl",
    REPO_ROOT / "artifacts" / "governance" / "notion_tool_audit.jsonl",
)
VIOLATIONS_LOG = REPO_ROOT / "artifacts" / "ci" / "notion_decision_parity_violations.jsonl"
BYPASS_LOG = REPO_ROOT / "artifacts" / "ci" / "notion_decision_parity_bypass.jsonl"

sys.path.insert(0, str(REPO_ROOT / ".claude" / "governance" / "scripts"))
from _notion_constants import (  # noqa: E402
    AUTHOR_GATE_LEDGER_DB_ID as AUTHOR_GATE_DB_ID,  # Archived ledger write-ID (reference only)
)


def _ledger_path() -> Path | None:
    if LEDGER_CURSOR.is_file():
        return LEDGER_CURSOR
    if LEDGER_WINDSURF.is_file():
        return LEDGER_WINDSURF
    return None


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


def _count_sqlite_decisions(window_days: int) -> int:
    ledger = _ledger_path()
    if ledger is None:
        return 0
    cutoff = (datetime.now(timezone.utc) - timedelta(days=window_days)).isoformat(timespec="seconds")
    try:
        conn = sqlite3.connect(f"file:{ledger}?mode=ro", uri=True, timeout=5)
    except sqlite3.Error:
        return 0
    try:
        row = conn.execute("SELECT COUNT(*) FROM decisions WHERE created_at >= ?", (cutoff,)).fetchone()
        return int(row[0]) if row else 0
    except sqlite3.Error:
        return 0
    finally:
        conn.close()


def _count_legacy_notion_posts(window_days: int) -> int:
    """Count successful Notion post-page calls to the archived Author-Gate DB in audit logs."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)
    count = 0
    for audit_path in NOTION_AUDIT_PATHS:
        if not audit_path.is_file():
            continue
        try:
            with audit_path.open("r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if AUTHOR_GATE_DB_ID not in line and "author_gate_decision" not in line.lower():
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    ts_str = obj.get("timestamp") or obj.get("ts") or ""
                    try:
                        if ts_str.endswith("Z"):
                            ts_str = ts_str[:-1] + "+00:00"
                        ts = datetime.fromisoformat(ts_str)
                        if ts.tzinfo is None:
                            ts = ts.replace(tzinfo=timezone.utc)
                        if ts < cutoff:
                            continue
                    except ValueError:
                        continue
                    op = (obj.get("tool") or obj.get("operation") or "").lower()
                    status = (obj.get("status") or obj.get("result") or "").lower()
                    if "post-page" in op or "post_page" in op or "post" in op:
                        if "ok" in status or "success" in status or status == "":
                            count += 1
        except OSError:
            continue
    return count


def main() -> int:
    ap = argparse.ArgumentParser(description="NP16 Author-Gate ledger signals (SQLite SSOT; Notion ledger archived)")
    ap.add_argument("--window-days", type=int, default=7)
    ap.add_argument(
        "--max-drift-pct",
        type=float,
        default=20.0,
        help="Deprecated (Notion ledger archived). Ignored unless legacy mode env set.",
    )
    ap.add_argument(
        "--absolute-tolerance",
        type=int,
        default=2,
        help="Deprecated (Notion ledger archived). Ignored unless legacy mode env set.",
    )
    args = ap.parse_args()

    if os.environ.get("NOTION_DECISION_PARITY_BYPASS") == "1":
        _log(BYPASS_LOG, {"reason": "env"})
        print("[check_notion_decision_parity] BYPASS (env). Logged.", file=sys.stderr)
        return 0

    sqlite_count = _count_sqlite_decisions(args.window_days)
    notion_count = _count_legacy_notion_posts(args.window_days)

    print(
        f"[check_notion_decision_parity] window={args.window_days}d "
        f"sqlite_decisions={sqlite_count} legacy_notion_author_gate_posts={notion_count}",
        file=sys.stderr,
    )
    print(
        "[check_notion_decision_parity] INFO: Author-Gate Notion ledger archived 2026-05-02; "
        "SQLite under .claude/state/refactor_decisions/ is SSOT. Drift vs Notion is not evaluated.",
        file=sys.stderr,
    )

    fail_closed = os.environ.get("NOTION_DECISION_PARITY_FAIL_CLOSED") == "1"
    if fail_closed and notion_count > 0:
        print(
            f"[check_notion_decision_parity] FAIL — fail-closed: {notion_count} legacy Notion "
            "Author-Gate post(s) in window (writes to archived DB)",
            file=sys.stderr,
        )
        _log(
            VIOLATIONS_LOG,
            {
                "sqlite_count": sqlite_count,
                "legacy_notion_posts": notion_count,
                "window_days": args.window_days,
            },
        )
        return 1

    if notion_count > 0:
        print(
            f"[check_notion_decision_parity] WARN: {notion_count} legacy Notion Author-Gate post(s) "
            "in audit window (expected 0 after archive)",
            file=sys.stderr,
        )

    print("[check_notion_decision_parity] OK — advisory", file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (sqlite3.Error, OSError) as exc:
        print(f"[check_notion_decision_parity] script error: {exc}", file=sys.stderr)
        sys.exit(2)
