#!/usr/bin/env python3
"""
check_ui_conformance.py — CI gate: Author-Gate UI conformance violations are
not stale-unresolved.

Tails artifacts/cursor/author_gate_ui_violations.jsonl and fails if any
non-bypass row within the staleness window (default 7 days) has not been
resolved (i.e., log tail still contains unresolved rows).

Exits:
    0 = log missing, empty, only bypass rows, or all rows are stale/aged out
    1 = unresolved violations within staleness window
    2 = unreadable log / IO error

Bypass: env AUTHOR_GATE_UI_CONFORMANCE_BYPASS=1 emits a warning and returns 0.

Follows the shape of ops_scripts/ci/author_gate/check_capture_queue_freshness.py
and other staleness gates.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
VIOLATIONS_LOG = REPO_ROOT / "artifacts" / "windsurf" / "author_gate_ui_violations.jsonl"
STALENESS_DAYS = int(os.environ.get("AUTHOR_GATE_UI_STALENESS_DAYS", "7"))


def _parse_ts(raw: str) -> datetime | None:
    try:
        # Accept "...+00:00" or "...Z"
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


def main() -> int:
    if os.environ.get("AUTHOR_GATE_UI_CONFORMANCE_BYPASS") == "1":
        print("[check_ui_conformance] BYPASS set — skipping", file=sys.stderr)
        return 0

    if not VIOLATIONS_LOG.exists():
        return 0

    try:
        rows = _load_rows(VIOLATIONS_LOG)
    except OSError as exc:
        print(f"[check_ui_conformance] could not read log: {exc}", file=sys.stderr)
        return 2

    if not rows:
        return 0

    cutoff = datetime.now(timezone.utc) - timedelta(days=STALENESS_DAYS)
    unresolved: list[dict[str, Any]] = []
    for row in rows:
        if row.get("reason") == "bypass":
            continue
        if row.get("resolved") is True:
            continue
        ts = _parse_ts(str(row.get("ts", "")))
        if ts is None:
            # Malformed timestamp — treat as recent to surface the problem
            unresolved.append(row)
            continue
        if ts >= cutoff:
            unresolved.append(row)

    if not unresolved:
        return 0

    print(
        f"[check_ui_conformance] {len(unresolved)} unresolved UI violations within "
        f"{STALENESS_DAYS}-day window. First 3:",
        file=sys.stderr,
    )
    for row in unresolved[:3]:
        print(f"  - {json.dumps(row, ensure_ascii=False)}", file=sys.stderr)
    print(
        "Resolve by fixing the ask_user_question UI to match packet.routing, then "
        "append {\"resolved\": true} rows or rotate the log.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
