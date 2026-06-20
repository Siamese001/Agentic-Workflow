#!/usr/bin/env python3
"""Post-write hook for the repo `.mcp.json`.

Behavior:
1. Detect whether `.mcp.json` was just modified.
2. Validate strict JSON.
3. Refresh the repo MCP Quick Reference if the SSOT changed.
4. Refresh the repo-root `AGENTS.md` MCP Quick Reference section.

Note: the repo SSOT is `.mcp.json`.

This hook is advisory. It never blocks the write.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from sync_mcp_config import (
    REPO_CONFIG,
    GLOBAL_CONFIG,
    AGENTS_MD,
    load_repo_config,
    validate_config,
    sync_agents_md,
    sync_global_config,
)

# Backward-compatible aliases used by tests/integrations.
SSOT = REPO_CONFIG
GLOBAL = GLOBAL_CONFIG


def _validate_ssot(path: Path = SSOT) -> list[str]:
    """Validate SSOT MCP config payload from a specific path."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"JSON parse error: {exc}"]
    if not isinstance(data, dict):
        return ["Invalid config: top-level JSON must be an object"]
    raw_issues = validate_config(data)
    issues: list[str] = []
    for issue in raw_issues:
        if issue == "Missing or invalid top-level 'mcpServers' object.":
            issues.append("Missing top-level 'mcpServers' key")
        elif "must define command, url, or serverUrl" in issue:
            normalized = issue.replace(
                "must define command, url, or serverUrl", "has neither 'command' nor 'url'"
            )
            issues.append(normalized.rstrip("."))
        else:
            issues.append(issue)

    servers = data.get("mcpServers", {})
    if isinstance(servers, dict):
        for name, cfg in servers.items():
            if not isinstance(cfg, dict):
                continue
            env = cfg.get("env")
            if not isinstance(env, dict):
                continue
            for _, value in env.items():
                if not isinstance(value, str):
                    continue
                lower = value.lower()
                if "localhost" in lower:
                    continue
                if value.startswith("sk-") or "api_key" in lower or "token" in lower:
                    issues.append(f"Server '{name}' has potential hardcoded secret in env")
                    break
    return issues


def _is_target_mcp_config_from_invocation() -> bool:
    """Return True when hook invocation context targets mcp.json, or is ambiguous."""
    if len(sys.argv) > 1:
        arg_path = str(sys.argv[1]).replace("\\", "/").lower()
        return arg_path.endswith("mcp.json")

    try:
        payload_raw = sys.stdin.read()
    except OSError:
        return True
    if not payload_raw.strip():
        return True
    try:
        payload = json.loads(payload_raw)
    except json.JSONDecodeError:
        return True
    if not isinstance(payload, dict):
        return True
    file_path = str(payload.get("file_path", "")).replace("\\", "/").lower()
    if not file_path:
        return True
    return file_path.endswith("mcp.json")


def _was_recent_write(path: Path, window_seconds: int = 10) -> bool:
    if not path.exists():
        return False
    try:
        return (time.time() - path.stat().st_mtime) <= window_seconds
    except (OSError, TypeError, ValueError):
        return True


def main() -> int:
    # Standalone-invocation guard: avoid indefinite hang when invoked via
    # `run_command` / pwsh (inherited stdin never receives EOF). Hook path
    # pipes stdin, which is never a TTY, so hook behavior is unaffected.
    if sys.stdin.isatty():
        return 0
    if not _is_target_mcp_config_from_invocation():
        return 0
    if not _was_recent_write(SSOT):
        return 0
    issues = _validate_ssot(SSOT)
    if issues:
        print("[mcp_sync] VALIDATION FAILED — not syncing:", flush=True)
        for issue in issues:
            print(f"  - {issue}", flush=True)
        return 0

    try:
        data = json.loads(SSOT.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("SSOT payload must be a JSON object")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"[mcp_sync] VALIDATION FAILED — JSON parse error: {exc}", flush=True)
        return 0

    try:
        copied = sync_global_config(data, GLOBAL)
        if copied:
            print(f"[mcp_sync] Synced {len(data['mcpServers'])} servers to repo SSOT cache.", flush=True)
        else:
            print("[mcp_sync] No-op: repo SSOT already current.", flush=True)
    except (OSError, ValueError) as exc:
        print(f"[mcp_sync] WARNING: global sync failed: {exc}", flush=True)

    try:
        if sync_agents_md():
            print(f"[mcp_sync] Refreshed AGENTS.md MCP Quick Reference at {AGENTS_MD}", flush=True)
        else:
            print("[mcp_sync] AGENTS.md not found — skipped AGENTS sync.", flush=True)
    except (OSError, ValueError) as exc:
        print(f"[mcp_sync] WARNING: AGENTS sync failed: {exc}", flush=True)

    # MCP Registry archived 2026-05-02 (notion-integration-consistency-audit-b2c4d8 W2).
    # Notion sync removed; `.mcp.json` is the SSOT.

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
