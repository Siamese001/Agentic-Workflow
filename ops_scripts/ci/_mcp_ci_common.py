"""Shared MCP CI helpers for Cursor and Windsurf editor configs."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
CURSOR_MCP_PATH = REPO_ROOT / ".cursor" / "mcp.json"
WINDSURF_MCP_PATH = REPO_ROOT / "docs/archive/windsurf/legacy-tree" / "mcp_config.json"
AGENTS_MD = REPO_ROOT / "AGENTS.md"
CURSOR_SYNC_SCRIPT_DIR = REPO_ROOT / ".claude" / "governance/scripts"
WINDSURF_SYNC_SCRIPT_DIR = REPO_ROOT / ".claude" / "governance/scripts" / "_legacy_windsurf"

PLAYWRIGHT_ALIASES = frozenset({"playwright", "io.windsurf/mcp-playwright"})

CURSOR_REQUIRED_SERVERS: frozenset[str] = frozenset({
    "GitKraken",
    "adg_sqlite",
    "deepwiki",
    "memory",
    "vector_db",
    "otel_mcp",
    "pytest_mcp",
    "redis",
    "notion",
    "tavily",
    "context7",
    "playwright",
})

WINDSURF_REQUIRED_SERVERS: frozenset[str] = frozenset({
    "GitKraken",
    "adg_sqlite",
    "deepwiki",
    "memory",
    "vector_db",
    "otel_mcp",
    "pytest_mcp",
    "redis",
    "notion",
    "tavily",
    "context7",
    "io.windsurf/mcp-playwright",
})

OPTIONAL_SERVERS: frozenset[str] = frozenset({
    "filesystem",
    "task_manager",
})

VALID_TOP_KEYS: frozenset[str] = frozenset({
    "_note",
    "mcpServers",
    "_bootstrap_env",
})

VALID_SERVER_KEYS: frozenset[str] = frozenset({
    "command",
    "args",
    "env",
    "disabled",
    "url",
    "type",
    "transport",
    "_note",
    "_comment",
    "_startup",
    "_shadow_disable",
    "_tuning_note",
    "_auth",
})

MCP_PROFILES: dict[str, frozenset[str]] = {
    "cursor": CURSOR_REQUIRED_SERVERS,
    "windsurf": WINDSURF_REQUIRED_SERVERS,
}


def profile_config_path(profile: str, windsurf_path: Path | None = None) -> Path:
    if profile == "cursor":
        return CURSOR_MCP_PATH
    return windsurf_path if windsurf_path is not None else WINDSURF_MCP_PATH


def canonical_server_id(server_id: str) -> str:
    if server_id in PLAYWRIGHT_ALIASES:
        return "playwright"
    return server_id


def canonical_server_set(server_ids: set[str] | frozenset[str]) -> set[str]:
    return {canonical_server_id(name) for name in server_ids}


def import_cursor_sync():
    if str(CURSOR_SYNC_SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(CURSOR_SYNC_SCRIPT_DIR))
    import sync_mcp_config  # noqa: WPS433

    return sync_mcp_config


def load_mcp_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} does not contain a JSON object")
    return data


def server_env_value(config: dict[str, Any], key: str) -> str:
    env = config.get("env", {})
    if not isinstance(env, dict):
        return ""
    value = env.get(key, "")
    return value if isinstance(value, str) else ""
