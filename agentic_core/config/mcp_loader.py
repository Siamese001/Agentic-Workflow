"""MCP Configuration Loader - Single Source of Truth for MCP Servers.

This module provides the canonical interface for loading and accessing MCP server
configuration from config/mcp_servers.yaml. All components should use this loader
instead of hardcoded configurations.

Example:
    from agentic_core.config.mcp_loader import MCPLoader

    loader = MCPLoader()
    config = loader.load()

    # Get tool mapping
    tool_fn = loader.get_tool_function("http_get")

    # Get server by prefix
    http_server = loader.get_server_by_prefix("mcp4")
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

try:
    from pydantic import BaseModel, Field, validator
except ImportError:
    BaseModel = object
    def Field(*a, **k):
        return None

    def validator(*a, **k):
        def decorator(f):
            return f
        return decorator


# Default path to the SSOT configuration
# Calculate from this file's location: agentic_core/config/mcp_loader.py -> ../../config/mcp_servers.yaml
DEFAULT_CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "mcp_servers.yaml"


class MCPTool(BaseModel):
    """Individual MCP tool definition."""

    target: str
    description: str
    aliases: list[str] = Field(default_factory=list)

    class Config:
        extra = "forbid"


class MCPServer(BaseModel):
    """MCP server configuration."""

    name: str
    prefix: str
    enabled: bool = True
    target_layer: str
    description: str
    command: str | None = None
    args: list[str] = Field(default_factory=list)
    cwd: str | None = None
    env: dict[str, str] = Field(default_factory=dict)
    capabilities: list[str] = Field(default_factory=list)
    tools: dict[str, MCPTool] = Field(default_factory=dict)

    @validator("prefix")
    def validate_prefix(cls, v: str) -> str:
        """Ensure prefix follows mcpN format."""
        if not v.startswith("mcp") or not v[3:].isdigit():
            raise ValueError(f"Invalid prefix format: {v}. Expected mcpN format.")
        return v

    @validator("target_layer")
    def validate_layer(cls, v: str) -> str:
        """Ensure layer is valid L0-L6."""
        valid_layers = {f"L{i}" for i in range(7)}
        if v not in valid_layers:
            raise ValueError(f"Invalid layer: {v}. Must be one of {valid_layers}")
        return v

    def get_tool(self, name: str) -> MCPTool | None:
        """Get tool by name or alias."""
        # Direct lookup
        if name in self.tools:
            return self.tools[name]

        # Search aliases
        for tool in self.tools.values():
            if name in tool.aliases:
                return tool

        return None

    class Config:
        extra = "allow"  # Allow _comment fields


class MCPConfig(BaseModel):
    """Root MCP configuration."""

    schema_version: str
    last_updated: str
    description: str
    servers: dict[str, MCPServer]
    tool_aliases: dict[str, str] = Field(default_factory=dict)
    validation: dict[str, Any] | None = None

    @property
    def total_tools(self) -> int:
        """Count total tools across all servers."""
        return sum(len(s.tools) for s in self.servers.values())

    @property
    def enabled_servers(self) -> dict[str, MCPServer]:
        """Get only enabled servers."""
        return {k: v for k, v in self.servers.items() if v.enabled}

    class Config:
        extra = "forbid"


class MCPLoader:
    """Loader for MCP configuration from YAML SSOT.

    This class provides caching, validation, and convenient access methods
    for MCP server configuration.

    Args:
        config_path: Path to mcp_servers.yaml. Defaults to config/mcp_servers.yaml
        hot_reload: If True, checks file modification time on each load()
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
        self._cache: MCPConfig | None = None
        self._last_mtime: float | None = None

        if not self.config_path.exists():
            raise FileNotFoundError(
                f"MCP config not found: {self.config_path}\n"
                f"Expected SSOT at: {DEFAULT_CONFIG_PATH}",
            )

    def load(self) -> MCPConfig:
        """Load and validate MCP configuration from YAML.

        Returns:
            Validated MCPConfig object

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid
            yaml.YAMLError: If YAML parsing fails
        """
        # Check if we can use cached version
        if self.cache_enabled and self._cache is not None:
            if not self.hot_reload:
                return self._cache

            # Hot reload: check modification time
            current_mtime = self.config_path.stat().st_mtime
            if current_mtime == self._last_mtime:
                return self._cache

        # Load from disk
        with open(self.config_path, encoding='utf-8') as f:
            raw_yaml = f.read()

        data = yaml.safe_load(raw_yaml) if yaml else self._manual_parse(raw_yaml)

        # Validate with Pydantic
        config = MCPConfig(**data)

        # Update cache
        if self.cache_enabled:
            self._cache = config
            self._last_mtime = self.config_path.stat().st_mtime

        return config

    def reload(self) -> MCPConfig:
        """Force reload from disk, bypassing cache."""
        self._cache = None
        self._last_mtime = None
        return self.load()

    def get_server(self, name: str) -> MCPServer | None:
        """Get server by name."""
        config = self.load()
        return config.servers.get(name)

    def get_server_by_prefix(self, prefix: str) -> MCPServer | None:
        """Get server by prefix (e.g., 'mcp4')."""
        config = self.load()
        for server in config.servers.values():
            if server.prefix == prefix:
                return server
        return None

    def get_servers_by_layer(self, layer: str) -> list[MCPServer]:
        """Get all servers assigned to a specific layer (L0-L6)."""
        config = self.load()
        return [s for s in config.servers.values() if s.target_layer == layer and s.enabled]

    def get_servers_by_capability(self, capability: str) -> list[MCPServer]:
        """Get all servers providing a specific capability."""
        config = self.load()
        return [
            s for s in config.servers.values()
            if capability in s.capabilities and s.enabled
        ]

    def get_tool_mapping(self) -> dict[str, str]:
        """Build complete tool dispatch table.

        Returns:
            Dictionary mapping logical tool names to MCP tool function names
            (e.g., {"http_get": "mcp4_http_get", ...})
        """
        config = self.load()
        mapping = {}

        for server in config.servers.values():
            if not server.enabled:
                continue

            for tool_name, tool in server.tools.items():
                # Add primary mapping
                mapping[tool_name] = tool.target

                # Add aliases
                for alias in tool.aliases:
                    mapping[alias] = tool.target

        # Add global aliases
        for alias, target_name in config.tool_aliases.items():
            # Resolve target name to actual function
            if target_name in mapping:
                mapping[alias] = mapping[target_name]

        return mapping

    def get_tool_function(self, tool_name: str) -> str | None:
        """Get the MCP function name for a logical tool.

        Args:
            tool_name: Logical tool name (e.g., "http_get")

        Returns:
            MCP function name (e.g., "mcp4_http_get") or None
        """
        mapping = self.get_tool_mapping()
        return mapping.get(tool_name)

    def resolve_tool(self, tool_name: str) -> str | None:
        """Alias for get_tool_function."""
        return self.get_tool_function(tool_name)

    def validate(self) -> list[str]:
        """Validate the configuration and return list of issues.

        Returns:
            List of validation error messages (empty if valid)
        """
        issues = []

        try:
            config = self.load()
        except FileNotFoundError as e:
            return [f"Config file not found: {e}"]
        except ImportError as e:
            return [f"Missing dependency: {e}"]
        except ValueError as e:
            return [f"Config validation error: {e}"]
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            # Catch YAML parsing errors and other unexpected issues
            if "yaml" in type(e).__module__.lower():
                return [f"YAML parsing error: {e}"]
            raise  # Re-raise unexpected exceptions

        # Check for duplicate tool names
        tool_names: dict[str, str] = {}
        for server_name, server in config.servers.items():
            for tool_name in server.tools.keys():
                if tool_name in tool_names:
                    issues.append(
                        f"Duplicate tool name '{tool_name}' in {server_name} "
                        f"(first defined in {tool_names[tool_name]})",
                    )
                else:
                    tool_names[tool_name] = server_name

        # Check for orphaned aliases
        for alias, target in config.tool_aliases.items():
            found = False
            for server in config.servers.values():
                if target in server.tools or any(
                    target in t.aliases for t in server.tools.values()
                ):
                    found = True
                    break
            if not found:
                issues.append(f"Orphaned alias '{alias}' -> '{target}' (target not found)")

        return issues

    def _manual_parse(self, raw: str) -> dict[str, Any]:
        """Fallback parser if PyYAML not available (basic implementation)."""
        raise ImportError(
            "PyYAML is required for MCP config loading.\n"
            "Install: pip install pyyaml",
        )


# Convenience functions for direct usage

def get_loader() -> MCPLoader:
    """Get default loader instance."""
    return MCPLoader()


def get_tool_mapping() -> dict[str, str]:
    """Get complete tool dispatch table."""
    return get_loader().get_tool_mapping()


def resolve_tool(tool_name: str) -> str | None:
    """Resolve logical tool name to MCP function name."""
    return get_loader().resolve_tool(tool_name)


# Module-level cache for performance
_loader_instance: MCPLoader | None = None


def get_cached_loader() -> MCPLoader:
    """Get or create cached loader instance."""
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = MCPLoader(cache_enabled=True)
    return _loader_instance
