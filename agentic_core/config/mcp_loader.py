"""MCP Configuration Loader - Single Source of Truth for MCP Servers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / ".windsurf" / "mcp_config.json"


class MCPServerEntry:
    """A single mcpServers entry from .windsurf/mcp_config.json."""

    def __init__(self, name: str, data: dict[str, Any]) -> None:
        self.name = name
        self.command: str | None = data.get("command") if isinstance(data.get("command"), str) else None
        self.url: str | None = data.get("url") if isinstance(data.get("url"), str) else None
        self.args: list[str] = (
            [str(arg) for arg in data.get("args", [])] if isinstance(data.get("args", []), list) else []
        )
        raw_env = data.get("env", {})
        self.env: dict[str, str] = (
            {str(k): str(v) for k, v in raw_env.items()} if isinstance(raw_env, dict) else {}
        )
        self.disabled: bool = bool(data.get("disabled", False))

    @property
    def enabled(self) -> bool:
        return not self.disabled


class MCPLoader:
    """Loader for MCP configuration from .windsurf/mcp_config.json."""

    def __init__(
        self,
        config_path: str | Path | None = None,
        hot_reload: bool = False,
        cache_enabled: bool = True,
    ):
        self.config_path = Path(config_path).expanduser().resolve() if config_path else DEFAULT_CONFIG_PATH
        self.hot_reload = hot_reload
        self.cache_enabled = cache_enabled
        self._cache: dict[str, MCPServerEntry] | None = None
        self._last_mtime_ns: int | None = None

        if not self.config_path.is_file():
            raise FileNotFoundError(
                f"MCP config not found: {self.config_path}\nExpected SSOT at: {DEFAULT_CONFIG_PATH}"
            )

    def load(self) -> dict[str, MCPServerEntry]:
        if self.cache_enabled and self._cache is not None:
            if not self.hot_reload:
                return self._cache
            if self.config_path.stat().st_mtime_ns == self._last_mtime_ns:
                return self._cache

        try:
            with self.config_path.open(encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid MCP config JSON: {self.config_path}: {exc}") from exc

        raw_servers = data.get("mcpServers", {})
        if not isinstance(raw_servers, dict):
            raise ValueError(f"mcpServers must be an object in {self.config_path}")

        entries = {
            name: MCPServerEntry(name, cfg)
            for name, cfg in raw_servers.items()
            if isinstance(name, str) and isinstance(cfg, dict)
        }

        if self.cache_enabled:
            self._cache = entries
            self._last_mtime_ns = self.config_path.stat().st_mtime_ns

        return entries

    def reload(self) -> dict[str, MCPServerEntry]:
        self._cache = None
        self._last_mtime_ns = None
        return self.load()

    def get_server(self, name: str) -> MCPServerEntry | None:
        return self.load().get(name)

    def list_servers(self) -> list[str]:
        return list(self.load().keys())

    def list_enabled_servers(self) -> list[str]:
        return [n for n, e in self.load().items() if e.enabled]

    def validate(self) -> list[str]:
        issues: list[str] = []
        try:
            entries = self.load()
        except (FileNotFoundError, ValueError) as exc:
            return [str(exc)]

        for name, entry in entries.items():
            if bool(entry.command) == bool(entry.url):
                issues.append(f"Server '{name}' must define exactly one of 'command' or 'url'")
            if entry.command and not entry.args:
                issues.append(f"Server '{name}' uses 'command' but has no 'args' entry")
        return issues


def get_loader() -> MCPLoader:
    return MCPLoader()


_loader_cache: dict[str, MCPLoader] = {}


def get_cached_loader() -> MCPLoader:
    if "default" not in _loader_cache:
        _loader_cache["default"] = MCPLoader(cache_enabled=True)
    return _loader_cache["default"]
