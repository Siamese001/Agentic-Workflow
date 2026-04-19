#!/usr/bin/env python3
"""Post-write hook for `.windsurf/mcp_config.json`.

Behavior:
1. Detect whether `.windsurf/mcp_config.json` was just modified.
2. Validate strict JSON.
3. Sync the repo SSOT to `~/.codeium/windsurf/mcp_config.json`.
4. Refresh the repo-root `AGENTS.md` MCP Quick Reference section.
5. Optionally upsert the Notion MCP Registry when `NOTION_TOKEN` is present.

This hook is advisory. It never blocks the write.
"""

from __future__ import annotations

import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any, cast

from sync_mcp_config import (
    REPO_CONFIG,
    GLOBAL_CONFIG,
    AGENTS_MD,
    load_notion_databases,
    load_repo_config,
    validate_config,
    sync_agents_md,
    sync_global_config,
)

# Backward-compatible aliases used by tests/integrations.
SSOT = REPO_CONFIG
GLOBAL = GLOBAL_CONFIG


def _resolve_mcp_registry_db_id() -> str | None:
    """Pull the MCP Registry DB ID from config/notion_databases.yaml.

    Returns None when the YAML is missing or the `mcp_registry` entry is absent,
    in which case the Notion sync step is skipped (never silently target a wrong
    database).
    """
    try:
        payload = load_notion_databases()
    except (FileNotFoundError, OSError, ValueError):
        return None
    for db in payload.get("databases", []):
        if db.get("key") == "mcp_registry":
            db_id = db.get("id")
            return str(db_id) if db_id is not None else None
    return None


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
    """Return True when hook invocation context targets mcp_config.json, or is ambiguous."""
    if len(sys.argv) > 1:
        arg_path = str(sys.argv[1]).replace("\\", "/").lower()
        return arg_path.endswith("mcp_config.json")

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
    return file_path.endswith("mcp_config.json")


_notion_api = "https://api.notion.com/v1"
_notion_version = "2022-06-28"
# Fallback DB ID for legacy environments that predate config/notion_databases.yaml.
# Prefer the YAML-resolved ID (see _resolve_mcp_registry_db_id) in main().
_legacy_fallback_db_id = "59693bbc71b14c63bc9fb31eb8b08a0e"


def _was_recent_write(path: Path, window_seconds: int = 10) -> bool:
    if not path.exists():
        return False
    try:
        return (time.time() - path.stat().st_mtime) <= window_seconds
    except (OSError, TypeError, ValueError):
        return True


def _notion_request(
    method: str, path: str, token: str, payload: dict[str, Any] | None = None
) -> dict[str, Any]:
    url = f"{_notion_api}{path}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": _notion_version,
            "Content-Type": "application/json",
        },
        method=method,
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return cast(dict[str, Any], json.loads(resp.read().decode("utf-8")))


def _derive_transport(cfg: dict[str, Any]) -> str:
    if "serverUrl" in cfg:
        return "serverUrl"
    if "url" in cfg:
        return "url"
    return "command"


def _derive_status(cfg: dict[str, Any]) -> str:
    return "Disabled" if cfg.get("disabled") is True else "Active"


def _find_existing_row(token: str, db_id: str, server_name: str) -> str | None:
    payload = {"filter": {"property": "Server Name", "title": {"equals": server_name}}}
    try:
        result = _notion_request("POST", f"/databases/{db_id}/query", token, payload)
        results = result.get("results", [])
        return results[0]["id"] if results else None
    except (urllib.error.URLError, OSError, json.JSONDecodeError, ValueError, KeyError):
        return None


def _upsert_server_row(token: str, db_id: str, name: str, transport: str, status: str, today: str) -> str:
    page_id = _find_existing_row(token, db_id, name)
    if page_id:
        payload = {
            "properties": {
                "Transport": {"select": {"name": transport}},
                "Status": {"select": {"name": status}},
                "Last Validated": {"date": {"start": today}},
            }
        }
        try:
            _notion_request("PATCH", f"/pages/{page_id}", token, payload)
            return "updated"
        except (urllib.error.URLError, OSError, json.JSONDecodeError, ValueError) as exc:
            print(f"[mcp_sync] Notion update failed for '{name}': {exc}", flush=True)
            return "skipped"
    payload = {
        "parent": {"database_id": db_id},
        "properties": {
            "Server Name": {"title": [{"text": {"content": name}}]},
            "Transport": {"select": {"name": transport}},
            "Status": {"select": {"name": status}},
            "Last Validated": {"date": {"start": today}},
            "Capability Scope": {"rich_text": [{"text": {"content": "(auto-synced — review and fill)"}}]},
        },
    }
    try:
        _notion_request("POST", "/pages", token, payload)
        return "created"
    except (urllib.error.URLError, OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"[mcp_sync] Notion create failed for '{name}': {exc}", flush=True)
        return "skipped"


def _sync_notion_mcp_registry(servers: dict[str, Any], token: str, db_id: str) -> None:
    today = date.today().isoformat()
    updated = created = skipped = 0
    for name, cfg in servers.items():
        outcome = _upsert_server_row(token, db_id, name, _derive_transport(cfg), _derive_status(cfg), today)
        if outcome == "updated":
            updated += 1
        elif outcome == "created":
            created += 1
        else:
            skipped += 1
    print(
        f"[mcp_sync] Notion MCP Registry: {updated} updated, {created} created, {skipped} skipped.",
        flush=True,
    )


def main() -> int:
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
        copied = sync_global_config(data)
        if copied:
            print(f"[mcp_sync] Synced {len(data['mcpServers'])} servers to global config.", flush=True)
        else:
            print(
                "[mcp_sync] No-op: repo SSOT and global config are the same file (symlink in place).",
                flush=True,
            )
    except (OSError, ValueError) as exc:
        print(f"[mcp_sync] WARNING: global sync failed: {exc}", flush=True)

    try:
        if sync_agents_md():
            print(f"[mcp_sync] Refreshed AGENTS.md MCP Quick Reference at {AGENTS_MD}", flush=True)
        else:
            print("[mcp_sync] AGENTS.md not found — skipped AGENTS sync.", flush=True)
    except (OSError, ValueError) as exc:
        print(f"[mcp_sync] WARNING: AGENTS sync failed: {exc}", flush=True)

    token = os.environ.get("NOTION_TOKEN", "").strip()
    if token:
        db_id_env = os.environ.get("NOTION_MCP_DATABASE_ID", "").strip()
        db_id_yaml = _resolve_mcp_registry_db_id()
        db_id = db_id_env or db_id_yaml or _legacy_fallback_db_id
        if not db_id_env and not db_id_yaml:
            print(
                "[mcp_sync] WARNING: Notion DB ID resolved via legacy fallback; "
                "ensure config/notion_databases.yaml has an 'mcp_registry' entry.",
                flush=True,
            )
        try:
            _sync_notion_mcp_registry(data.get("mcpServers", {}), token, db_id)
        except (urllib.error.URLError, OSError, json.JSONDecodeError, ValueError) as exc:
            print(f"[mcp_sync] WARNING: Notion sync failed: {exc}", flush=True)
    else:
        print("[mcp_sync] Notion sync skipped: NOTION_TOKEN not set.", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
