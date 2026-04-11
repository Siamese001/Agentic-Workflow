"""Post-write hook: sync .windsurf/mcp_config.json -> ~/.codeium/windsurf/mcp_config.json.

Phase 1: copy to global Windsurf config (existing behaviour).
Phase 2: upsert MCP Registry rows in Notion (advisory — never blocks the write).

Triggered by hooks.json post_write_code when .windsurf/mcp_config.json is written.
Stdlib only — no external dependencies.

Exit 0 always (sync failure is advisory, never blocks the write).

Environment variables (Phase 2):
  NOTION_TOKEN               — Notion internal integration token (secret_…).
                               If absent, Phase 2 is skipped with advisory output.
  NOTION_MCP_DATABASE_ID     — Notion MCP Registry database ID.
                               Defaults to the pilot database: 59693bbc71b14c63bc9fb31eb8b08a0e
"""

from __future__ import annotations

import io
import json
import os
import shutil
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path
from typing import cast

REPO_ROOT = Path(__file__).resolve().parents[2]
SSOT = REPO_ROOT / ".windsurf" / "mcp_config.json"
GLOBAL = Path.home() / ".codeium" / "windsurf" / "mcp_config.json"


def _validate_ssot(path: Path) -> list[str]:
    """Basic sanity checks before copying — catches malformed edits early."""
    issues: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return [f"JSON parse error: {exc}"]

    if "mcpServers" not in data:
        issues.append("Missing top-level 'mcpServers' key")
    else:
        servers = data["mcpServers"]
        for name, cfg in servers.items():
            if not isinstance(cfg, dict):
                continue
            if not cfg.get("command") and not cfg.get("url") and not cfg.get("serverUrl"):
                issues.append(f"Server '{name}' has neither 'command', 'url', nor 'serverUrl'")
            env = cfg.get("env", {})
            for key, val in env.items():
                if not isinstance(val, str) or val.startswith("${"):
                    continue
                key_upper = key.upper()
                is_secret_key = any(kw in key_upper for kw in ("KEY", "TOKEN", "SECRET", "PASSWORD", "API"))
                is_localhost = "localhost" in val or "127.0.0.1" in val
                if is_secret_key and not is_localhost and len(val) > 8:
                    issues.append(f"Server '{name}' env '{key}' looks like a hardcoded secret")
    return issues


# ---------------------------------------------------------------------------
# Phase 2 — Notion MCP Registry sync (advisory, stdlib urllib only)
# ---------------------------------------------------------------------------

_NOTION_API = "https://api.notion.com/v1"
_NOTION_VERSION = "2022-06-28"
_DEFAULT_DB_ID = "59693bbc71b14c63bc9fb31eb8b08a0e"


def _notion_request(
    method: str,
    path: str,
    token: str,
    payload: dict | None = None,
) -> dict:
    """Make a Notion REST API call. Raises urllib.error.URLError / HTTPError on failure."""
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
        return cast(dict, json.loads(resp.read().decode("utf-8")))


def _derive_transport(cfg: dict) -> str:
    """Derive Transport select value from server config dict."""
    if "serverUrl" in cfg:
        return "serverUrl"
    if "url" in cfg:
        return "url"
    return "command"


def _derive_status(cfg: dict) -> str:
    """Derive Status select value from disabled flag."""
    return "Disabled" if cfg.get("disabled") is True else "Active"


def _find_existing_row(token: str, db_id: str, server_name: str) -> str | None:
    """Search Notion MCP Registry for a row matching server_name. Returns page_id or None."""
    payload = {
        "filter": {
            "property": "Server Name",
            "title": {"equals": server_name},
        }
    }
    try:
        result = _notion_request("POST", f"/databases/{db_id}/query", token, payload)
        results = result.get("results", [])
        return results[0]["id"] if results else None
    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        json.JSONDecodeError,
        KeyError,
        IndexError,
        OSError,
    ):
        return None


def _upsert_server_row(
    token: str,
    db_id: str,
    name: str,
    transport: str,
    status: str,
    today: str,
) -> str:
    """Upsert one server row. Returns 'updated', 'created', or 'skipped'."""
    page_id = _find_existing_row(token, db_id, name)

    if page_id:
        update_payload: dict = {
            "properties": {
                "Transport": {"select": {"name": transport}},
                "Status": {"select": {"name": status}},
                "Last Validated": {"date": {"start": today}},
            }
        }
        try:
            _notion_request("PATCH", f"/pages/{page_id}", token, update_payload)
            return "updated"
        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError) as exc:
            print(f"[mcp_sync] Notion: WARNING — update failed for '{name}': {exc}", flush=True)
            return "skipped"
    else:
        create_payload: dict = {
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
            _notion_request("POST", "/pages", token, create_payload)
            return "created"
        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError) as exc:
            print(f"[mcp_sync] Notion: WARNING — create failed for '{name}': {exc}", flush=True)
            return "skipped"


def _sync_notion_mcp_registry(servers: dict, token: str, db_id: str) -> None:
    """Upsert MCP Registry rows for each server. Advisory output only."""
    today = date.today().isoformat()
    updated = created = skipped = 0

    for name, cfg in servers.items():
        transport = _derive_transport(cfg)
        status = _derive_status(cfg)
        outcome = _upsert_server_row(token, db_id, name, transport, status, today)
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
    # Path filtering: only run when the written file is mcp_config.json.
    # Previously handled by file_pattern in hooks.json (non-standard field now removed).
    if len(sys.argv) > 1:
        written_path = sys.argv[1]
        if not written_path.replace("\\", "/").endswith("mcp_config.json"):
            return 0
    else:
        # No argv: attempt to read file_path from stdin JSON payload.
        raw = sys.stdin.read()
        if raw.strip():
            try:
                payload = json.loads(raw)
                file_path = (
                    payload.get("tool_info", payload).get("file_path", "")
                    if isinstance(payload, dict)
                    else ""
                )
                if file_path and not file_path.replace("\\", "/").endswith("mcp_config.json"):
                    return 0
            except (json.JSONDecodeError, AttributeError):
                pass
        sys.stdin = io.StringIO("")  # stdin consumed; replace for safety

    if not SSOT.exists():
        print(f"[mcp_sync] SSOT not found: {SSOT} — skipping", flush=True)
        return 0

    issues = _validate_ssot(SSOT)
    if issues:
        print("[mcp_sync] VALIDATION FAILED — not copying to global:", flush=True)
        for issue in issues:
            print(f"  - {issue}", flush=True)
        print(f"[mcp_sync] Fix {SSOT} and save again.", flush=True)
        return 0  # advisory only — never block the write

    servers: dict = {}
    try:
        GLOBAL.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(SSOT), str(GLOBAL))
        servers = json.loads(SSOT.read_text(encoding="utf-8")).get("mcpServers", {})
        print(
            f"[mcp_sync] Synced {len(servers)} servers to global config. Restart Windsurf to apply.",
            flush=True,
        )
    except OSError as exc:
        print(f"[mcp_sync] WARNING: copy failed: {exc}", flush=True)
        print(
            f"[mcp_sync] Manually copy: {SSOT} -> {GLOBAL}",
            flush=True,
        )

    # Phase 2 — Notion MCP Registry sync (advisory only)
    notion_token = os.environ.get("NOTION_TOKEN", "").strip()
    if not notion_token:
        print("[mcp_sync] Notion sync skipped: NOTION_TOKEN not set.", flush=True)
        return 0

    if not servers:
        print("[mcp_sync] Notion sync skipped: no servers parsed from config.", flush=True)
        return 0

    notion_db_id = os.environ.get("NOTION_MCP_DATABASE_ID", _DEFAULT_DB_ID).strip()
    _sync_notion_mcp_registry(servers, notion_token, notion_db_id)

    return 0


if __name__ == "__main__":
    sys.exit(main())
