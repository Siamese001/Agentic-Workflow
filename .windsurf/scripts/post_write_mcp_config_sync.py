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
    AGENTS_MD,
    load_repo_config,
    validate_config,
    sync_agents_md,
    sync_global_config,
)

_NOTION_API = "https://api.notion.com/v1"
_NOTION_VERSION = "2022-06-28"
_DEFAULT_DB_ID = "59693bbc71b14c63bc9fb31eb8b08a0e"


def _was_recent_write(path: Path, window_seconds: int = 10) -> bool:
    if not path.exists():
        return False
    return (time.time() - path.stat().st_mtime) <= window_seconds


def _notion_request(
    method: str, path: str, token: str, payload: dict[str, Any] | None = None
) -> dict[str, Any]:
    url = f"{_NOTION_API}{path}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": _NOTION_VERSION,
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
    except Exception:
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
        except Exception as exc:
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
    except Exception as exc:
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
    sys.stdin = io.StringIO("")
    if not _was_recent_write(REPO_CONFIG):
        return 0
    try:
        data = load_repo_config()
    except Exception as exc:
        print(f"[mcp_sync] VALIDATION FAILED — JSON parse error: {exc}", flush=True)
        return 0

    issues = validate_config(data)
    if issues:
        print("[mcp_sync] VALIDATION FAILED — not syncing:", flush=True)
        for issue in issues:
            print(f"  - {issue}", flush=True)
        return 0

    try:
        sync_global_config(data)
        print(f"[mcp_sync] Synced {len(data['mcpServers'])} servers to global config.", flush=True)
    except Exception as exc:
        print(f"[mcp_sync] WARNING: global sync failed: {exc}", flush=True)

    try:
        if sync_agents_md():
            print(f"[mcp_sync] Refreshed AGENTS.md MCP Quick Reference at {AGENTS_MD}", flush=True)
        else:
            print("[mcp_sync] AGENTS.md not found — skipped AGENTS sync.", flush=True)
    except Exception as exc:
        print(f"[mcp_sync] WARNING: AGENTS sync failed: {exc}", flush=True)

    token = os.environ.get("NOTION_TOKEN", "").strip()
    if token:
        db_id = os.environ.get("NOTION_MCP_DATABASE_ID", _DEFAULT_DB_ID).strip()
        try:
            _sync_notion_mcp_registry(data.get("mcpServers", {}), token, db_id)
        except Exception as exc:
            print(f"[mcp_sync] WARNING: Notion sync failed: {exc}", flush=True)
    else:
        print("[mcp_sync] Notion sync skipped: NOTION_TOKEN not set.", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
