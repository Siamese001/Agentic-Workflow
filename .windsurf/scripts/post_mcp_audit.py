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
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

FAIL_POLICY = "open"

REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_LOG = REPO_ROOT / "artifacts" / "windsurf" / "mcp_tool_audit.jsonl"
GITKRAKEN_WRITE_AUDIT_LOG = REPO_ROOT / "artifacts" / "windsurf" / "gitkraken_write_audit.jsonl"
SESSION_STATE = REPO_ROOT / "artifacts" / "windsurf" / "session_state.json"

GITKRAKEN_SERVER_NAME = "GitKraken"

# Write-capable GitKraken tools requiring enriched audit records
_GITKRAKEN_WRITE_TOOLS: set[str] = {
    "git_add_or_commit",
    "git_checkout",
    "git_stash",
    "git_worktree",
    "git_branch",
    "gitlens_commit_composer",
    "gitlens_start_work",
    "git_push",
    "pull_request_create",
    "pull_request_create_review",
    "issues_add_comment",
    "gitlens_start_review",
}


def _git_context(repo: Path) -> dict:
    """
    Capture lightweight git context for audit records.
    Fail-open: any subprocess failure returns partial context.
    Constitutional §14: timeout=. §0: shell=False.
    """
    ctx: dict = {"repo": str(repo)}
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            shell=False,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(repo),
        )
        ctx["branch"] = r.stdout.strip() if r.returncode == 0 else "unknown"
    except (OSError, subprocess.TimeoutExpired):
        ctx["branch"] = "unknown"

    try:
        r = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            shell=False,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(repo),
        )
        ctx["commit"] = r.stdout.strip() if r.returncode == 0 else "unknown"
    except (OSError, subprocess.TimeoutExpired):
        ctx["commit"] = "unknown"

    return ctx


def _append_gitkraken_write_audit(record: dict) -> None:
    try:
        GITKRAKEN_WRITE_AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(GITKRAKEN_WRITE_AUDIT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except OSError:
        pass


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


def _mark_task_started() -> None:
    """Set task_started=true and increment update_task_count. Fail-open on any error."""
    try:
        if SESSION_STATE.exists():
            state = json.loads(SESSION_STATE.read_text(encoding="utf-8"))
        else:
            state = {}
        state["task_started"] = True
        count = state.get("update_task_count", 0) + 1
        state["update_task_count"] = count
        if count >= 2:
            state["lessons_captured"] = True
        SESSION_STATE.write_text(json.dumps(state), encoding="utf-8")
    except (OSError, json.JSONDecodeError):
        pass  # fail-open


def _mark_task_decomposed() -> None:
    """Set task_decomposed=true in session state. Fail-open on any error."""
    try:
        if SESSION_STATE.exists():
            state = json.loads(SESSION_STATE.read_text(encoding="utf-8"))
        else:
            state = {}
        state["task_decomposed"] = True
        SESSION_STATE.write_text(json.dumps(state), encoding="utf-8")
    except (OSError, json.JSONDecodeError):
        pass  # fail-open


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

    # Track task_manager lifecycle state transitions.
    if "task" in server_name.lower():
        if tool_name == "create_task":
            _mark_task_created()
        elif tool_name == "update_task":
            _mark_task_started()
        elif tool_name == "decompose_task":
            _mark_task_decomposed()

    # GitKraken write-action enriched audit (P0-5 / P1-2)
    if server_name == GITKRAKEN_SERVER_NAME and tool_name in _GITKRAKEN_WRITE_TOOLS:
        repo = REPO_ROOT
        ctx = _git_context(repo)
        write_record = {
            "timestamp": record["timestamp"],
            "tool": tool_name,
            "duration_ms": duration_ms,
            "repo": ctx.get("repo"),
            "branch": ctx.get("branch"),
            "commit": ctx.get("commit"),
        }
        _append_gitkraken_write_audit(write_record)

    return 0


if __name__ == "__main__":
    sys.exit(main())
