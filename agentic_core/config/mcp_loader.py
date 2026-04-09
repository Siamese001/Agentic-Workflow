"""MCP Configuration Loader - Single Source of Truth for MCP Servers.

Reads .windsurf/mcp_config.json (Windsurf mcpServers format) — the single SSOT
for all MCP server definitions.  Do NOT read config/mcp_servers.yaml (archived).

Example:
    from agentic_core.config.mcp_loader import MCPLoader

    loader = MCPLoader()
    servers = loader.list_servers()   # ["GitKraken", "adg_sqlite", ...]
    entry   = loader.get_server("adg_sqlite")  # {"command": ..., "args": ...}
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


# SSOT: .windsurf/mcp_config.json  (Windsurf mcpServers format)
# agentic_core/config/mcp_loader.py -> ../../.windsurf/mcp_config.json
DEFAULT_CONFIG_PATH = Path(__file__).parent.parent.parent / ".windsurf" / "mcp_config.json"


# ---------------------------------------------------------------------------
# Windsurf mcpServers entry — matches .windsurf/mcp_config.json schema exactly
# ---------------------------------------------------------------------------
class MCPServerEntry:
    """A single mcpServers entry from .windsurf/mcp_config.json."""

    def __init__(self, name: str, data: dict[str, Any]) -> None:
        self.name = name
        self.command: str | None = data.get("command")
        self.url: str | None = data.get("url")
        self.args: list[str] = data.get("args", [])
        self.env: dict[str, str] = data.get("env", {})
        self.disabled: bool = data.get("disabled", False)

    @property
    def enabled(self) -> bool:
        return not self.disabled


class MCPLoader:
    """Loader for MCP configuration from .windsurf/mcp_config.json (Windsurf format).

    Reads the mcpServers dict directly — no YAML, no schema translation.

    Args:
        config_path: Path to mcp_config.json. Defaults to .windsurf/mcp_config.json
        hot_reload: If True, re-reads on mtime change
        cache_enabled: If True, caches loaded config in memory
    """

    def __init__(
        self,
        config_path: str | Path | None = None,
        hot_reload: bool = False,
        cache_enabled: bool = True,
    ):
        self.config_path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
        self.hot_reload = hot_reload
        self.cache_enabled = cache_enabled
        self._cache: dict[str, MCPServerEntry] | None = None
        self._last_mtime: float | None = None

        if not self.config_path.exists():
            raise FileNotFoundError(
                f"MCP config not found: {self.config_path}\nExpected SSOT at: {DEFAULT_CONFIG_PATH}",
            )

    def load(self) -> dict[str, MCPServerEntry]:
        """Load mcpServers from .windsurf/mcp_config.json.

        Returns:
            Dict mapping server name -> MCPServerEntry
        """
        if self.cache_enabled and self._cache is not None:
            if not self.hot_reload:
                return self._cache
            if self.config_path.stat().st_mtime == self._last_mtime:
                return self._cache

        with open(self.config_path, encoding="utf-8") as f:
            data = json.load(f)

        raw_servers: dict[str, Any] = data.get("mcpServers", {})
        entries = {
            name: MCPServerEntry(name, cfg) for name, cfg in raw_servers.items() if isinstance(cfg, dict)
        }

        if self.cache_enabled:
            self._cache = entries
            self._last_mtime = self.config_path.stat().st_mtime

        return entries

    def reload(self) -> dict[str, MCPServerEntry]:
        """Force reload from disk, bypassing cache."""
        self._cache = None
        self._last_mtime = None
        return self.load()

    def get_server(self, name: str) -> MCPServerEntry | None:
        """Get a server entry by name (e.g. 'adg_sqlite')."""
        return self.load().get(name)

    def list_servers(self) -> list[str]:
        """Return names of all servers (enabled and disabled)."""
        return list(self.load().keys())

    def list_enabled_servers(self) -> list[str]:
        """Return names of enabled servers only."""
        return [n for n, e in self.load().items() if e.enabled]

    def validate(self) -> list[str]:
        """Return list of validation issues (empty = valid)."""
        issues: list[str] = []
        try:
            entries = self.load()
        except FileNotFoundError as exc:
            return [f"Config file not found: {exc}"]
        except ValueError as exc:
            return [f"Config parse error: {exc}"]

        for name, entry in entries.items():
            if not entry.command and not entry.url:
                issues.append(f"Server '{name}' has neither 'command' nor 'url'")
        return issues


# Convenience functions


def get_loader() -> MCPLoader:
    """Get default loader instance."""
    return MCPLoader()


# Module-level cache for performance
_loader_cache: dict[str, MCPLoader] = {}


def get_cached_loader() -> MCPLoader:
    """Get or create cached loader instance."""
    if "default" not in _loader_cache:
        _loader_cache["default"] = MCPLoader(cache_enabled=True)
    return _loader_cache["default"]
