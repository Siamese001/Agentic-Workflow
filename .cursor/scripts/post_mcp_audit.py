#!/usr/bin/env python3
"""
post_mcp_audit.py — Cursor post_mcp_tool_use advisory telemetry hook (Phase 1.7).

Reads JSON payload from stdin. Payload fields:
  tool_info.mcp_server_name  — name of MCP server called
  tool_info.mcp_tool_name    — name of tool called
  tool_info.duration_ms      — response time in milliseconds (optional)

Behavior (ADVISORY ONLY — always exits 0):
  - Appends telemetry record to artifacts/cursor/mcp_tool_audit.jsonl
  - Records: server, tool, timestamp, duration_ms

Fail policy: OPEN — any error → exit 0 silently.
Zero hardcoded paths — repo_root resolved from __file__.
"""

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

fail_policy = "open"

repo_root = Path(__file__).resolve().parents[2]
audit_log = repo_root / "artifacts" / "cursor" / "mcp_tool_audit.jsonl"
gitkraken_write_audit_log = repo_root / "artifacts" / "cursor" / "gitkraken_write_audit.jsonl"
# Supply-chain drift detection for MCP servers (W2 hardening).
# Tracks SHA256 of mcpServers block + per-server (command, args, env keys)
# between sessions. Writes a drift record whenever the fingerprint changes.
mcp_config_path = repo_root / ".cursor" / "mcp.json"
mcp_fingerprint_path = repo_root / "artifacts" / "cursor" / "mcp_config_fingerprint.json"
mcp_drift_log = repo_root / "artifacts" / "cursor" / "mcp_drift.jsonl"
# Namespaced per logical session — matches pre_mcp_gate.py and pre_prompt_classifier.py.
_session_id = os.environ.get("VSCODE_PID") or str(os.getppid())
session_state = repo_root / "artifacts" / "cursor" / f"session_state_{_session_id}.json"

gitkraken_server_name = "GitKraken"
notion_server_name = "notion"
notion_audit_log = repo_root / "artifacts" / "cursor" / "notion_tool_audit.jsonl"

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
    except (
        OSError,
        json.JSONDecodeError,
    ):  # guardian: allow-silent-swallow -- notion session state: non-fatal, fail-open
        pass  # fail-open


def _append_notion_audit(record: dict) -> None:
    try:
        notion_audit_log.parent.mkdir(parents=True, exist_ok=True)
        with open(notion_audit_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except OSError:  # guardian: allow-silent-swallow -- notion audit log: non-fatal, fail-open
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
    except OSError:  # guardian: allow-silent-swallow -- gitkraken audit log: non-fatal, fail-open
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
    except (
        OSError,
        json.JSONDecodeError,
    ):  # guardian: allow-silent-swallow -- task created state: non-fatal, fail-open
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
    except (
        OSError,
        json.JSONDecodeError,
    ):  # guardian: allow-silent-swallow -- task started state: non-fatal, fail-open
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
    except (
        OSError,
        json.JSONDecodeError,
    ):  # guardian: allow-silent-swallow -- task decomposed state: non-fatal, fail-open
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
    except (
        OSError,
        json.JSONDecodeError,
    ):  # guardian: allow-silent-swallow -- memory recalled state: non-fatal, fail-open
        pass  # fail-open


def _append_log(record: dict) -> None:
    try:
        audit_log.parent.mkdir(parents=True, exist_ok=True)
        with open(audit_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except OSError:  # guardian: allow-silent-swallow -- audit log append: non-fatal, fail-open
        pass


# ---------------------------------------------------------------------
# MCP supply-chain drift detection (W2)
# ---------------------------------------------------------------------


def _fingerprint_mcp_config() -> dict | None:
    """Compute SHA256 fingerprint of mcpServers block + per-server hashes.

    Returns None on any IO/parse error (caller fails-open).
    """
    try:
        with mcp_config_path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None

    servers = data.get("mcpServers", {})
    if not isinstance(servers, dict):
        return None

    overall = hashlib.sha256()
    overall.update(json.dumps(servers, sort_keys=True).encode("utf-8"))
    overall_hash = overall.hexdigest()

    per_server: dict[str, str] = {}
    for name, cfg in sorted(servers.items()):
        if not isinstance(cfg, dict):
            continue
        # Fingerprint command + args + env keys (NOT env values — those may be secrets)
        shape = {
            "command": cfg.get("command"),
            "args": cfg.get("args"),
            "url": cfg.get("url"),
            "env_keys": sorted(list((cfg.get("env") or {}).keys())),
            "disabled": bool(cfg.get("disabled", False)),
        }
        h = hashlib.sha256()
        h.update(json.dumps(shape, sort_keys=True).encode("utf-8"))
        per_server[name] = h.hexdigest()

    return {
        "mcpServers_sha256": overall_hash,
        "per_server": per_server,
        "server_count": len(per_server),
        "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def _append_drift_record(record: dict) -> None:
    try:
        mcp_drift_log.parent.mkdir(parents=True, exist_ok=True)
        with mcp_drift_log.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:  # guardian: allow-silent-swallow -- drift log append: non-fatal, fail-open
        pass


def _persist_fingerprint(fp: dict) -> None:
    try:
        mcp_fingerprint_path.parent.mkdir(parents=True, exist_ok=True)
        with mcp_fingerprint_path.open("w", encoding="utf-8") as fh:
            json.dump(fp, fh, indent=2, sort_keys=True)
    except OSError:  # guardian: allow-silent-swallow -- fingerprint persist: non-fatal, fail-open
        pass


def _check_mcp_config_drift() -> None:
    """Compare current mcp.json fingerprint against last stored one.

    On drift, append a JSONL record documenting what changed (added/removed/
    changed server names) and persist the new fingerprint.
    """
    current = _fingerprint_mcp_config()
    if current is None:
        return

    previous: dict | None = None
    if mcp_fingerprint_path.exists():
        try:
            with mcp_fingerprint_path.open("r", encoding="utf-8") as fh:
                previous = json.load(fh)
        except (OSError, json.JSONDecodeError):
            previous = None

    # First run — just persist, no drift record
    if previous is None:
        _persist_fingerprint(current)
        return

    if previous.get("mcpServers_sha256") == current.get("mcpServers_sha256"):
        return  # no drift

    prev_servers = previous.get("per_server", {}) or {}
    curr_servers = current.get("per_server", {}) or {}
    added = sorted(set(curr_servers) - set(prev_servers))
    removed = sorted(set(prev_servers) - set(curr_servers))
    changed = sorted(
        name
        for name in set(prev_servers) & set(curr_servers)
        if prev_servers.get(name) != curr_servers.get(name)
    )

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "event": "mcp_config_drift",
        "previous_sha256": previous.get("mcpServers_sha256"),
        "current_sha256": current.get("mcpServers_sha256"),
        "previous_captured_at": previous.get("captured_at"),
        "servers_added": added,
        "servers_removed": removed,
        "servers_changed": changed,
        "server_count_before": previous.get("server_count"),
        "server_count_after": current.get("server_count"),
    }
    _append_drift_record(record)
    _persist_fingerprint(current)


def main() -> int:
    # Standalone-invocation guard: avoid indefinite hang when invoked via
    # `run_command` / pwsh (inherited stdin never receives EOF). Hook path
    # pipes stdin, which is never a TTY, so hook behavior is unaffected.
    if sys.stdin.isatty():
        return 0
    # Run supply-chain drift check first — cheap (hashes a small JSON file) and
    # writes to a separate JSONL so it doesn't interfere with telemetry.
    _check_mcp_config_drift()

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

    # W2.2 — mcp_invocation ledger: per-call latency + retry telemetry
    try:
        from tools.ledgers.hook_helpers import emit_ledger_event
        # Band by duration_ms: <500ms fast, <2000ms slow, >=2000ms hang-candidate
        if duration_ms is None:
            band = "unknown"
        elif duration_ms < 500:
            band = "fast"
        elif duration_ms < 2000:
            band = "slow"
        else:
            band = "hang"
        emit_ledger_event(
            ledger="mcp_invocation",
            event_kind="mcp_call",
            prediction={
                "server_id": server_name or "",
                "tool_name": tool_name or "",
            },
            outcome={
                "actual_latency_ms": duration_ms,
                "retries": 0,
                "hang_bypass_triggered": False,
            },
            score_band=band,
            score_numeric=float(duration_ms) if duration_ms is not None else None,
            latency_ms=int(duration_ms) if duration_ms is not None else None,
            repo_area=".cursor/scripts/post_mcp_audit.py",
        )
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- hook fail-soft contract
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
