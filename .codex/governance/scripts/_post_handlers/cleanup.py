"""Cleanup handler — log rotation for spawned-processes / mcp-audit logs.

In-process equivalent of `.codex/governance/scripts/post_agent_cleanup.py`. Always
exits 0 on error (fail-soft).
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import ParsedResponse


def _rotate(path: Path, keep: int) -> int:
    if not path.exists():
        return 0
    try:
        lines = path.read_text(encoding="utf-8").strip().splitlines()
        if len(lines) <= keep:
            return len(lines)
        kept = lines[-keep:]
        path.write_text("\n".join(kept) + "\n", encoding="utf-8")
        return len(kept)
    except OSError:
        return 0


def _count(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        return len(path.read_text(encoding="utf-8").strip().splitlines())
    except OSError:
        return 0


def run(parsed: ParsedResponse, repo_root: Path) -> None:
    ws = repo_root / "artifacts" / "governance"
    if not ws.exists():
        return

    limits = {
        ws / "spawned_processes.jsonl": 500,
        ws / "mcp_tool_audit.jsonl": 500,
        ws / "mcp_lint_audit.jsonl": 200,
    }

    kept = {}
    for path, k in limits.items():
        kept[path.name] = _rotate(path, k)

    summary = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "via": "dispatcher",
        "lines_kept": kept,
    }
    try:
        (ws / "session_summary.json").write_text(
            json.dumps(summary, indent=2), encoding="utf-8"
        )
    except OSError as err:
        print(f"[cleanup] session_summary write failed: {err}", file=sys.stderr)
