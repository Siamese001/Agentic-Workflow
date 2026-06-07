#!/usr/bin/env python3
"""
check_ask_user_question_packet_freshness.py — CI gate.

Plan: author-gate-four-req-enforcement-c4d2a8 W2.P1.

Tails ``artifacts/cursor/ask_user_question_packet_violations.jsonl`` (produced
by ``post_agent_ask_user_question_packet_audit.py``) and fails when any
non-bypass row within the staleness window (default 7 days) has not been
resolved.

Sibling to ``check_ui_conformance.py`` — same shape, different log. Closes
GAP-2 from the plan: the vacuum-closure runtime audit was previously unwatched
by CI, so accumulating critical-severity rows ("ask_user_question + no packet
+ high decision-density") could go unnoticed.

Exits:
    0 = log missing, empty, only bypass rows, or all rows aged out / resolved
    1 = unresolved violations within staleness window
    2 = unreadable log / IO error

Bypass: ``ASK_PACKET_AUDIT_FRESHNESS_BYPASS=1`` emits a warning and returns 0.
Window override: ``ASK_PACKET_STALENESS_DAYS`` (int, default 7).
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
VIOLATIONS_LOG = (
    REPO_ROOT / "artifacts" / "windsurf" / "ask_user_question_packet_violations.jsonl"
)
DEFAULT_STALENESS_DAYS = 7


def _staleness_days() -> int:
    raw = os.environ.get("ASK_PACKET_STALENESS_DAYS", str(DEFAULT_STALENESS_DAYS))
    try:
        value = int(raw)
    except ValueError:
        return DEFAULT_STALENESS_DAYS
    return value if value > 0 else DEFAULT_STALENESS_DAYS


def _parse_ts(raw: str) -> datetime | None:
    try:
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        return datetime.fromisoformat(raw)
    except (ValueError, TypeError):
        return None


def _load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def evaluate(rows: list[dict[str, Any]], window_days: int) -> list[dict[str, Any]]:
    """Pure function. Return list of unresolved-within-window rows."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)
    unresolved: list[dict[str, Any]] = []
    for row in rows:
        if row.get("reason") == "bypass":
            continue
        if row.get("resolved") is True:
            continue
        ts = _parse_ts(str(row.get("ts", "")))
        if ts is None:
            unresolved.append(row)
            continue
        if ts >= cutoff:
            unresolved.append(row)
    return unresolved


def main() -> int:
    if os.environ.get("ASK_PACKET_AUDIT_FRESHNESS_BYPASS") == "1":
        print(
            "[check_ask_user_question_packet_freshness] BYPASS set — skipping",
            file=sys.stderr,
        )
        return 0

    if not VIOLATIONS_LOG.exists():
        return 0

    try:
        rows = _load_rows(VIOLATIONS_LOG)
    except OSError as exc:
        print(
            f"[check_ask_user_question_packet_freshness] could not read log: {exc}",
            file=sys.stderr,
        )
        return 2

    if not rows:
        return 0

    window = _staleness_days()
    unresolved = evaluate(rows, window)
    if not unresolved:
        return 0

    print(
        f"[check_ask_user_question_packet_freshness] {len(unresolved)} unresolved "
        f"vacuum-closure violations within {window}-day window. First 3:",
        file=sys.stderr,
    )
    for row in unresolved[:3]:
        print(f"  - {json.dumps(row, ensure_ascii=False)}", file=sys.stderr)
    print(
        "Resolve by emitting an AUTHOR_GATE_PACKET before the offending "
        "ask_user_question (use .claude/skills/author-gate-packet-builder/"
        "emit_packet.py), then append {\"resolved\": true} rows or rotate the log.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
