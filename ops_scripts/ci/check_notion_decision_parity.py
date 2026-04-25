#!/usr/bin/env python3
"""
check_notion_decision_parity.py — W5.1 Notion ↔ SQLite decision parity.

Weekly reconciliation: count decisions in the local SQLite ledger within
--window-days vs the Notion Author-Gate Decision Ledger DB. Alarm when
drift exceeds --max-drift-pct.

Uses the Notion audit log (artifacts/windsurf/notion_tool_audit.jsonl) as
the parity signal — counts successful API-post-page calls to the Author-Gate
Decision Ledger database_id. This avoids requiring a live Notion API key
at CI time (fail-closed without auth would be worse than log-based audit).

Exit 0 — within tolerance (or both sides empty)
Exit 1 — drift exceeds tolerance
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
LEDGER_DB = REPO_ROOT / ".windsurf" / "state" / "refactor_decisions" / "refactor_decision_ledger.sqlite"
NOTION_AUDIT = REPO_ROOT / "artifacts" / "windsurf" / "notion_tool_audit.jsonl"
VIOLATIONS_LOG = REPO_ROOT / "artifacts" / "windsurf" / "notion_decision_parity_violations.jsonl"
BYPASS_LOG = REPO_ROOT / "artifacts" / "windsurf" / "notion_decision_parity_bypass.jsonl"

AUTHOR_GATE_DB_ID = "18bb9145-1320-4191-8b14-6c309776bcf5"  # Author-Gate Decision Ledger write-ID


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
    if not LEDGER_DB.exists():
        return 0
    cutoff = (datetime.now(timezone.utc) - timedelta(days=window_days)).isoformat(timespec="seconds")
    try:
        conn = sqlite3.connect(f"file:{LEDGER_DB}?mode=ro", uri=True, timeout=5)
    except sqlite3.Error:
        return 0
    try:
        row = conn.execute("SELECT COUNT(*) FROM decisions WHERE created_at >= ?", (cutoff,)).fetchone()
        return int(row[0]) if row else 0
    except sqlite3.Error:
        return 0
    finally:
        conn.close()


def _count_notion_posts(window_days: int) -> int:
    """Count successful Notion API-post-page calls to the Author-Gate DB."""
    if not NOTION_AUDIT.exists():
        return 0
    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)
    count = 0
    try:
        with NOTION_AUDIT.open("r", encoding="utf-8", errors="replace") as fh:
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
        return 0
    return count


def main() -> int:
    ap = argparse.ArgumentParser(description="Notion ↔ SQLite decision parity (W5.1)")
    ap.add_argument("--window-days", type=int, default=7)
    ap.add_argument(
        "--max-drift-pct", type=float, default=20.0, help="Tolerate this %% divergence before failing"
    )
    ap.add_argument(
        "--absolute-tolerance",
        type=int,
        default=2,
        help="Always tolerate this absolute delta (covers in-flight)",
    )
    args = ap.parse_args()

    if os.environ.get("NOTION_DECISION_PARITY_BYPASS") == "1":
        _log(BYPASS_LOG, {"reason": "env"})
        print("[check_notion_decision_parity] BYPASS (env). Logged.", file=sys.stderr)
        return 0

    sqlite_count = _count_sqlite_decisions(args.window_days)
    notion_count = _count_notion_posts(args.window_days)

    print(
        f"[check_notion_decision_parity] window={args.window_days}d "
        f"sqlite={sqlite_count} notion={notion_count}",
        file=sys.stderr,
    )

    if sqlite_count == 0 and notion_count == 0:
        print("[check_notion_decision_parity] OK — both empty", file=sys.stderr)
        return 0

    delta = abs(sqlite_count - notion_count)
    denom = max(sqlite_count, notion_count, 1)
    drift_pct = (delta / denom) * 100.0

    if delta <= args.absolute_tolerance:
        print(
            f"[check_notion_decision_parity] OK — delta={delta} within "
            f"absolute tolerance {args.absolute_tolerance}",
            file=sys.stderr,
        )
        return 0

    if drift_pct <= args.max_drift_pct:
        print(
            f"[check_notion_decision_parity] OK — drift {drift_pct:.1f}% within max {args.max_drift_pct}%",
            file=sys.stderr,
        )
        return 0

    print(
        f"[check_notion_decision_parity] FAIL — drift {drift_pct:.1f}% "
        f"(delta={delta}) exceeds max {args.max_drift_pct}%",
        file=sys.stderr,
    )
    _log(
        VIOLATIONS_LOG,
        {
            "sqlite_count": sqlite_count,
            "notion_count": notion_count,
            "delta": delta,
            "drift_pct": drift_pct,
            "window_days": args.window_days,
        },
    )
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (sqlite3.Error, OSError) as exc:
        print(f"[check_notion_decision_parity] script error: {exc}", file=sys.stderr)
        sys.exit(2)
