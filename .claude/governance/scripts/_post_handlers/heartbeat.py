"""Heartbeat handler — writes one line per response to the heartbeat log.

In-process replacement for the old standalone post-agent heartbeat hook.
Mirrors that script's contract exactly so the standalone hook can be
removed once the dispatcher is fully cut over.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

from . import ParsedResponse

_MAX_LINES = 500


def _previous_timestamp(path: Path) -> float | None:
    if not path.exists():
        return None
    try:
        tail = path.read_text(encoding="utf-8").splitlines()[-1]
        obj = json.loads(tail)
        ts = obj.get("timestamp_unix")
        if isinstance(ts, (int, float)):
            return float(ts)
    except (OSError, ValueError, IndexError):
        return None
    return None


def _truncate(path: Path, max_lines: int) -> None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        if len(lines) > max_lines:
            kept = lines[-max_lines:]
            path.write_text("\n".join(kept) + "\n", encoding="utf-8")
    except OSError as err:
        print(f"[heartbeat] truncate failed: {err}", file=sys.stderr)


def run(parsed: ParsedResponse, repo_root: Path) -> None:
    """Append heartbeat record. Fail-soft."""
    artifacts = repo_root / "artifacts" / "governance"
    try:
        artifacts.mkdir(parents=True, exist_ok=True)
    except OSError as err:
        print(f"[heartbeat] mkdir failed: {err}", file=sys.stderr)
        return

    path = artifacts / "post_agent_heartbeat.jsonl"
    now = time.time()
    prev = _previous_timestamp(path)
    gap_ms = round((now - prev) * 1000.0, 2) if prev else None

    record = {
        "timestamp_unix": now,
        "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
        "gap_ms_since_prior": gap_ms,
        "pid": os.getpid(),
        "via": "dispatcher",
    }

    try:
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
    except OSError as err:
        print(f"[heartbeat] write failed: {err}", file=sys.stderr)
        return

    _truncate(path, _MAX_LINES)
