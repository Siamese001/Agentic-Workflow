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
Zero hardcoded paths — repo_root resolved from __file__.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

fail_policy = "open"

repo_root = Path(__file__).resolve().parents[2]
audit_log = repo_root / "artifacts" / "windsurf" / "mcp_tool_audit.jsonl"
gitkraken_write_audit_log = repo_root / "artifacts" / "windsurf" / "gitkraken_write_audit.jsonl"
# Namespaced per logical session — matches pre_mcp_gate.py and pre_prompt_classifier.py.
_SESSION_ID = os.environ.get("VSCODE_PID") or str(os.getppid())
session_state = repo_root / "artifacts" / "windsurf" / f"session_state_{_SESSION_ID}.json"

gitkraken_server_name = "GitKraken"
notion_server_name = "notion"
notion_audit_log = repo_root / "artifacts" / "windsurf" / "notion_tool_audit.jsonl"

# Notion tool classification — tool names as the MCP exposes them (without mcp6_ prefix)
_NOTION_WRITE_TOOLS: frozenset[str] = frozenset(
    {
        "API-post-page",
        "API-patch-page",
        "API-patch-block-children",
        "API-update-a-block",
        "API-create-a-data-source",
        "API-update-a-data-source",
        "API-delete-a-block",
        "API-move-page",
        "API-create-a-comment",
    }
)
_NOTION_READ_TOOLS: frozenset[str] = frozenset(
    {
        "API-retrieve-a-page",
        "API-get-block-children",
        "API-retrieve-a-block",
        "API-retrieve-a-database",
        "API-retrieve-a-data-source",
        "API-retrieve-a-page-property",
        "API-retrieve-a-comment",
        "API-post-search",
        "API-query-data-source",
        "API-list-data-source-templates",
        "API-get-self",
        "API-get-user",
        "API-get-users",
    }
)


def _classify_notion_tool(tool_name: str) -> str:
    """Return 'write', 'read', or 'unknown' for a notion tool name."""
    if tool_name in _NOTION_WRITE_TOOLS:
        return "write"
    if tool_name in _NOTION_READ_TOOLS:
        return "read"
    return "unknown"


def _mark_notion_called(tool_name: str, tool_class: str) -> None:
    """
    Track notion tool call in session state.

    Markers written:
      notion_last_called  — most recent notion tool + class + timestamp (notion selected + attempted)
      notion_last_write   — most recent write tool + timestamp (write attempted)
      notion_read_after_write — True when a read follows a write in the same session (refresh signal)

    Fail-open on any error.
    """
    try:
        state = json.loads(session_state.read_text(encoding="utf-8")) if session_state.exists() else {}
        ts = datetime.now(timezone.utc).isoformat()
        state["notion_last_called"] = {"tool": tool_name, "class": tool_class, "ts": ts}
        if tool_class == "write":
            state["notion_last_write"] = {"tool": tool_name, "ts": ts}
        elif tool_class == "read" and state.get("notion_last_write"):
            state["notion_read_after_write"] = True
        session_state.write_text(json.dumps(state), encoding="utf-8")
    except (OSError, json.JSONDecodeError):
        pass  # fail-open


def _append_notion_audit(record: dict) -> None:
    try:
        notion_audit_log.parent.mkdir(parents=True, exist_ok=True)
        with open(notion_audit_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except OSError:
        pass


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
        gitkraken_write_audit_log.parent.mkdir(parents=True, exist_ok=True)
        with open(gitkraken_write_audit_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except OSError:
        pass


def _mark_task_created() -> None:
    """Set task_created=true in session state. Fail-open on any error."""
    try:
        if session_state.exists():
            state = json.loads(session_state.read_text(encoding="utf-8"))
        else:
            state = {}
        state["task_created"] = True
        session_state.write_text(json.dumps(state), encoding="utf-8")
    except (OSError, json.JSONDecodeError):
        pass  # fail-open: don't disrupt audit on state file error


def _mark_task_started() -> None:
    """Set task_started=true and increment update_task_count. Fail-open on any error."""
    try:
        if session_state.exists():
            state = json.loads(session_state.read_text(encoding="utf-8"))
        else:
            state = {}
        state["task_started"] = True
        count = state.get("update_task_count", 0) + 1
        state["update_task_count"] = count
        if count >= 2:
            state["lessons_captured"] = True
        session_state.write_text(json.dumps(state), encoding="utf-8")
    except (OSError, json.JSONDecodeError):
        pass  # fail-open


def _mark_task_decomposed() -> None:
    """Set task_decomposed=true in session state. Fail-open."""
    try:
        if session_state.exists():
            state = json.loads(session_state.read_text(encoding="utf-8"))
        else:
            state = {}
        state["task_decomposed"] = True
        session_state.write_text(json.dumps(state), encoding="utf-8")
    except (OSError, json.JSONDecodeError):
        pass  # fail-open


def _mark_memory_recalled() -> None:
    """Set memory_recalled=True in session state when mem_recall_session_start is invoked.

    Signals to pre_prompt_classifier that memory has been recalled this session,
    suppressing the MEMORY RECALL REQUIRED mandate on subsequent turns.
    Fail-open on any error.
    """
    try:
        state = json.loads(session_state.read_text(encoding="utf-8")) if session_state.exists() else {}
        state["memory_recalled"] = True
        session_state.write_text(json.dumps(state), encoding="utf-8")
    except (OSError, json.JSONDecodeError):
        pass  # fail-open


def _append_log(record: dict) -> None:
    try:
        audit_log.parent.mkdir(parents=True, exist_ok=True)
        with open(audit_log, "a", encoding="utf-8") as f:
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

    # Track Memory MCP session recall — suppresses mandate on subsequent turns.
    if server_name == "memory" and tool_name == "mem_recall_session_start":
        _mark_memory_recalled()

    # Notion enriched audit: selection, class, duration-based status inference, read-after-write
    if server_name == notion_server_name:
        tool_class = _classify_notion_tool(tool_name)
        # Heuristic: API round-trips take >50 ms; <20 ms suggests immediate error (gate/auth/conn)
        if duration_ms is None:
            likely_status = "unknown"
        elif duration_ms < 20:
            likely_status = "suspect_error"
        else:
            likely_status = "likely_ok"
        notion_record = {
            "timestamp": record["timestamp"],
            "server": notion_server_name,
            "tool": tool_name,
            "class": tool_class,
            "duration_ms": duration_ms,
            "likely_status": likely_status,
        }
        _append_notion_audit(notion_record)
        _mark_notion_called(tool_name, tool_class)

    # GitKraken write-action enriched audit (P0-5 / P1-2)
    if server_name == gitkraken_server_name and tool_name in _GITKRAKEN_WRITE_TOOLS:
        repo = repo_root
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
