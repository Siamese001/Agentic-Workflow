#!/usr/bin/env python3
"""
post_mcp_audit.py — Windsurf post_mcp_tool_use advisory telemetry hook (Phase 1.7).

Reads JSON payload from stdin. Payload fields:
  tool_info.mcp_server_name  — name of MCP server called
  tool_info.mcp_tool_name    — name of tool called
  tool_info.duration_ms      — response time in milliseconds (optional)

Behavior (ADVISORY ONLY — always exits 0):
  - Appends telemetry record to artifacts/windsurf/mcp_tool_audit.jsonl
  - Records: server, tool, timestamp, duration_ms

Fail policy: OPEN — any error → exit 0 silently.
Zero hardcoded paths — REPO_ROOT resolved from __file__.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

FAIL_POLICY = "open"

REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_LOG = REPO_ROOT / "artifacts" / "windsurf" / "mcp_tool_audit.jsonl"
SESSION_STATE = REPO_ROOT / "artifacts" / "windsurf" / "session_state.json"


def _mark_task_created() -> None:
    """Set task_created=true in session state. Fail-open on any error."""
    try:
        if SESSION_STATE.exists():
            state = json.loads(SESSION_STATE.read_text(encoding="utf-8"))
        else:
            state = {}
        state["task_created"] = True
        SESSION_STATE.write_text(json.dumps(state), encoding="utf-8")
    except (OSError, json.JSONDecodeError):
        pass  # fail-open: don't disrupt audit on state file error


def _append_log(record: dict) -> None:
    try:
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(AUDIT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except OSError:
        pass


def main() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        return 0

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    if not isinstance(payload, dict):
        return 0

    tool_info = payload.get("tool_info", payload)
    if not isinstance(tool_info, dict):
        return 0

    server_name = tool_info.get("mcp_server_name", "")
    tool_name = tool_info.get("mcp_tool_name", "")
    duration_ms = tool_info.get("duration_ms", None)

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mcp_server_name": server_name,
        "mcp_tool_name": tool_name,
        "duration_ms": duration_ms,
    }
    _append_log(record)

    # Mark task_created when Cascade calls create_task on the task_manager MCP.
    if tool_name == "create_task" and "task" in server_name.lower():
        _mark_task_created()

    return 0


if __name__ == "__main__":
    sys.exit(main())
