#!/usr/bin/env python3
"""
check_adg_first_violations_freshness.py — CI gate (CF1).

Tails ``artifacts/governance/adg_first_violations.jsonl`` (produced by
``post_agent_adg_audit.py``) and fails when any non-bypass row within
the staleness window (default 7 days) has not been resolved.

Sibling to ``ops_scripts/ci/author_gate/check_ask_user_question_packet_freshness.py``
— same shape, different log. Closes the gap where ADG-first violations
(grep_search used for dependency analysis instead of ADG MCP) were written
by the legacy editor hook but never surfaced in CI.

Exits:
    0 = log missing, empty, only bypass rows, all rows aged out / resolved, or
        advisory mode with unresolved rows (default; drift logged to stderr).
    1 = unresolved violations within staleness window (fail-closed only)
    2 = unreadable log / IO error

Fail-closed: ``ADG_FIRST_VIOLATIONS_FRESHNESS_FAIL_CLOSED=1`` exits 1 when any
unresolved row remains in the staleness window.

Bypass: ``ADG_FIRST_VIOLATIONS_FRESHNESS_BYPASS=1`` emits a warning and returns 0.
Window override: ``ADG_FIRST_STALENESS_DAYS`` (int, default 7).

Constitutional refs: §28 (ADG over grep), §34 (retrieval budgets).
Sibling hook: ``.codex/governance/scripts/post_agent_adg_audit.py``.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
VIOLATIONS_LOG = REPO_ROOT / "artifacts" / "governance" / "adg_first_violations.jsonl"
DEFAULT_STALENESS_DAYS = 7


def _staleness_days() -> int:
    raw = os.environ.get("ADG_FIRST_STALENESS_DAYS", str(DEFAULT_STALENESS_DAYS))
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
    if os.environ.get("ADG_FIRST_VIOLATIONS_FRESHNESS_BYPASS") == "1":
        print(
            "[check_adg_first_violations_freshness] BYPASS set — skipping",
            file=sys.stderr,
        )
        return 0

    if not VIOLATIONS_LOG.exists():
        return 0

    try:
        rows = _load_rows(VIOLATIONS_LOG)
    except OSError as exc:
        print(
            f"[check_adg_first_violations_freshness] could not read log: {exc}",
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
        f"[check_adg_first_violations_freshness] {len(unresolved)} unresolved "
        f"ADG-first violations within {window}-day window. First 3:",
        file=sys.stderr,
    )
    for row in unresolved[:3]:
        print(f"  - {json.dumps(row, ensure_ascii=False)}", file=sys.stderr)
    print(
        "Resolve by using adg_sqlite MCP tools (adg_edge_fanin/fanout) instead of "
        "grep_search for dependency analysis, then append {\"resolved\": true} rows "
        "to the log or rotate it. Bypass: ADG_FIRST_VIOLATIONS_FRESHNESS_BYPASS=1.",
        file=sys.stderr,
    )
    if os.environ.get("ADG_FIRST_VIOLATIONS_FRESHNESS_FAIL_CLOSED", "").strip() == "1":
        return 1
    print(
        "[check_adg_first_violations_freshness] Advisory mode — violations present; "
        "exiting 0 (set ADG_FIRST_VIOLATIONS_FRESHNESS_FAIL_CLOSED=1 to fail closed).",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
