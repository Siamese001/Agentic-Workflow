"""Shared MCP CI helpers for the repo MCP config."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
REPO_MCP_PATH = REPO_ROOT / ".mcp.json"
AGENTS_MD = REPO_ROOT / "AGENTS.md"
REPO_SYNC_SCRIPT_DIR = REPO_ROOT / ".codex" / "governance" / "scripts"

PLAYWRIGHT_ALIASES = frozenset({"playwright"})

REPO_REQUIRED_SERVERS: frozenset[str] = frozenset({
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

MCP_PROFILES: dict[str, frozenset[str]] = {"repo": REPO_REQUIRED_SERVERS}


def profile_config_path(profile: str = "repo", mirror_path: Path | None = None) -> Path:
    del profile, mirror_path
    return REPO_MCP_PATH


def canonical_server_id(server_id: str) -> str:
    if server_id in PLAYWRIGHT_ALIASES:
        return "playwright"
    return server_id


def canonical_server_set(server_ids: set[str] | frozenset[str]) -> set[str]:
    return {canonical_server_id(name) for name in server_ids}


def import_repo_sync():
    if str(REPO_SYNC_SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(REPO_SYNC_SCRIPT_DIR))
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
