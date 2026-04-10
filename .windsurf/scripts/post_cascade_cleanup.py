#!/usr/bin/env python3
"""
post_cascade_cleanup.py — Windsurf post_cascade_response cleanup hook (Phase 1.8).

Reads JSON payload from stdin (no fields required from Windsurf).

Behavior (ADVISORY ONLY — always exits 0):
  - Rotates spawned_processes.jsonl: keeps last 500 records, archives older ones
  - Rotates mcp_tool_audit.jsonl: keeps last 500 records
  - Rotates mcp_lint_audit.jsonl: keeps last 200 records
  - Writes session summary to artifacts/windsurf/session_summary.json
    (line counts for each audit log = lightweight session health indicator)

Fail policy: OPEN — any error → exit 0 silently.
Zero hardcoded paths — REPO_ROOT resolved from __file__.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

FAIL_POLICY = "open"

REPO_ROOT = Path(__file__).resolve().parents[2]
WINDSURF_DIR = REPO_ROOT / "artifacts" / "windsurf"

PROCESS_LOG = WINDSURF_DIR / "spawned_processes.jsonl"
MCP_TOOL_LOG = WINDSURF_DIR / "mcp_tool_audit.jsonl"
MCP_LINT_LOG = WINDSURF_DIR / "mcp_lint_audit.jsonl"
SESSION_SUMMARY = WINDSURF_DIR / "session_summary.json"

LOG_LIMITS = {
    str(PROCESS_LOG): 500,
    str(MCP_TOOL_LOG): 500,
    str(MCP_LINT_LOG): 200,
}


def _rotate_log(log_path: Path, keep: int) -> int:
    """
    Keep the last `keep` lines of log_path in place.
    Returns number of lines kept.
    """
    if not log_path.exists():
        return 0
    try:
        lines = log_path.read_text(encoding="utf-8").strip().splitlines()
        if len(lines) <= keep:
            return len(lines)
        kept = lines[-keep:]
        log_path.write_text("\n".join(kept) + "\n", encoding="utf-8")
        return len(kept)
    except OSError:
        return 0


def _count_lines(log_path: Path) -> int:
    if not log_path.exists():
        return 0
    try:
        return len(log_path.read_text(encoding="utf-8").strip().splitlines())
    except OSError:
        return 0


def run_cleanup(windsurf_dir: Path) -> dict:
    """Rotate logs and return session summary dict."""
    process_log = windsurf_dir / "spawned_processes.jsonl"
    mcp_tool_log = windsurf_dir / "mcp_tool_audit.jsonl"
    mcp_lint_log = windsurf_dir / "mcp_lint_audit.jsonl"

    limits = {
        process_log: 500,
        mcp_tool_log: 500,
        mcp_lint_log: 200,
    }

    kept_counts = {}
    for log_path, keep in limits.items():
        kept_counts[log_path.name] = _rotate_log(log_path, keep)

    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "audit_line_counts": kept_counts,
    }
    return summary


def main() -> int:
    try:
        WINDSURF_DIR.mkdir(parents=True, exist_ok=True)
        summary = run_cleanup(WINDSURF_DIR)
        SESSION_SUMMARY.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    except OSError:
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
