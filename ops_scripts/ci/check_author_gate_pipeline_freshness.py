#!/usr/bin/env python3
"""
check_author_gate_pipeline_freshness.py — CI gate (AGP1).

Plan: author-gate-ui-renderer-hardening-a7f3c2 W3.P3.1.

Tails ``artifacts/windsurf/author_gate_pipeline_violations.jsonl`` (produced
by ``post_cascade_author_gate_pipeline_audit.py``) and fails when any
non-bypass row within the staleness window (default 7 days) has not been
resolved.

Sibling to ``check_ask_user_question_packet_freshness.py`` — same shape,
different log. Closes the **packet-without-ask** enforcement gap at CI level.

Exits:
    0 = log missing, empty, only bypass rows, or all rows aged out / resolved
    1 = unresolved violations within staleness window (fail-closed mode only)
    2 = unreadable log / IO error

Default mode: fail-closed (exits 1 on unresolved violations).
Advisory override: ``AG_PIPELINE_ADVISORY=1`` exits 0 even with violations.
Bypass: ``AG_PIPELINE_FRESHNESS_BYPASS=1`` emits a warning and returns 0.
Window override: ``AG_PIPELINE_STALENESS_DAYS`` (int, default 7).
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
VIOLATIONS_LOG = (
    REPO_ROOT / "artifacts" / "windsurf" / "author_gate_pipeline_violations.jsonl"
)
DEFAULT_STALENESS_DAYS = 7
GATE_NAME = "check_author_gate_pipeline_freshness"


def _staleness_days() -> int:
    raw = os.environ.get("AG_PIPELINE_STALENESS_DAYS", str(DEFAULT_STALENESS_DAYS))
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
    if os.environ.get("AG_PIPELINE_FRESHNESS_BYPASS") == "1":
        print(f"[{GATE_NAME}] BYPASS set — skipping", file=sys.stderr)
        return 0

    if not VIOLATIONS_LOG.exists():
        return 0

    try:
        rows = _load_rows(VIOLATIONS_LOG)
    except OSError as exc:
        print(f"[{GATE_NAME}] could not read log: {exc}", file=sys.stderr)
        return 2

    if not rows:
        return 0

    window = _staleness_days()
    unresolved = evaluate(rows, window)
    if not unresolved:
        return 0

    advisory = os.environ.get("AG_PIPELINE_ADVISORY") == "1"

    print(
        f"[{GATE_NAME}] {len(unresolved)} unresolved pipeline-completion "
        f"violations within {window}-day window. First 3:",
        file=sys.stderr,
    )
    for row in unresolved[:3]:
        print(f"  - {json.dumps(row, ensure_ascii=False)}", file=sys.stderr)
    print(
        "Resolve by ensuring every AUTHOR_GATE_PACKET: emission is followed "
        "by an ask_user_question call in the same response. See plan "
        "author-gate-ui-renderer-hardening-a7f3c2.",
        file=sys.stderr,
    )

    if advisory:
        print(
            f"[{GATE_NAME}] advisory mode — not blocking. Unset AG_PIPELINE_ADVISORY to enforce.",
            file=sys.stderr,
        )
        return 0

    # Fail-closed (default).
    return 1


if __name__ == "__main__":
    sys.exit(main())
