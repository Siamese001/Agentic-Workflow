"""
Tool Registry - Centralized SSOT for all tools.

Ensures tools reside in Sovereign Territory before registration.
Integrates with SovereignIndex for safety validation.
"""

import logging

from agentic_core.L5_safety.validators.structure_blueprint import (
    GLOBAL_EXCLUDED_DIRS,
    is_path_allowed,
)

Logger = logging.getLogger(__name__)


class tool_registry:
    """
    SSOT for all tools. Ensures tools reside in Sovereign Territory.

    Features:
    - Singleton pattern for global access
    - Path validation via is_path_allowed
    - Integration with SovereignIndex for tool discovery
    - Logging of registration attempts
    """

    _instance: Optional["tool_registry"] = None
    _tools: dict[str, dict[str, Any]] = {}

    def __new__(cls) -> "tool_registry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools = {}
        return cls._instance

    @classmethod
    def get_instance(cls) -> "tool_registry":
        """Get the singleton instance of tool_registry."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (for testing)."""
        cls._instance = None
        cls._tools = {}

    def register_tool(
        self, tool_name: str, tool_path: str, tool_func: Callable[..., Any], description: str = ""
    ) -> bool:
        """
        Registers a tool only after verifying its location is sovereign.

        Args:
            tool_name: Unique identifier for the tool
            tool_path: Path to the tool file (absolute or relative)
            tool_func: The callable function/method for the tool
            description: Optional description of the tool

        Returns:
            True if registration succeeded, False if rejected
        """
        try:
            path = Path(tool_path)
            if path.is_absolute():
                # Convert to relative path from cwd
                try:
                    rel_path = path.relative_to(Path.cwd())
                except ValueError:
                    # Path is not under cwd
                    Logger.error(
                        f"[REGISTRY] REJECTED: Tool '{tool_name}' at {tool_path} "
                        "is outside project root."
                    )
                    return False
            else:
                rel_path = path

            # Check if path is in globally excluded directories
            path_parts = rel_path.parts
            if any(excl in path_parts for excl in GLOBAL_EXCLUDED_DIRS):
                Logger.error(
                    f"[REGISTRY] REJECTED: Tool '{tool_name}' at {tool_path} "
                    "is in a globally excluded directory."
                )
                return False

            # Validate path is in Sovereign Territory
            if not is_path_allowed(str(rel_path)):
                Logger.error(
                    f"[REGISTRY] REJECTED: Tool '{tool_name}' at {tool_path} "
                    "is outside Sovereign Territory."
                )
                return False

            # Register the tool
            self._tools[tool_name] = {
                "path": str(tool_path),
                "func": tool_func,
                "verified": True,
                "description": description,
            }
            Logger.info(f"[REGISTRY] SUCCESS: Tool '{tool_name}' registered and verified.")
            return True

        except Exception as e:
            Logger.error(f"[REGISTRY] ERROR: Failed to register tool '{tool_name}': {e}")
            return False

    def unregister_tool(self, tool_name: str) -> bool:
        """
        Removes a tool from the registry.

        Args:
            tool_name: Name of the tool to remove

        Returns:
            True if removed, False if not found
        """
        if tool_name in self._tools:
            del self._tools[tool_name]
            Logger.info(f"[REGISTRY] Tool '{tool_name}' unregistered.")
            return True
        return False

    def get_tool(self, tool_name: str) -> dict[str, Any] | None:
        """
        Retrieves a registered tool by name.

        Args:
            tool_name: Name of the tool to retrieve

        Returns:
            Tool dict with path, func, verified, description or None
        """
        return self._tools.get(tool_name)

    def get_tool_func(self, tool_name: str) -> Callable[..., Any] | None:
        """
        Retrieves just the callable function for a tool.

        Args:
            tool_name: Name of the tool

        Returns:
            The tool's callable function or None
        """
        tool = self._tools.get(tool_name)
        return tool["func"] if tool else None

    def list_tools(self) -> list[str]:
        """Returns list of all registered tool names."""
        return list(self._tools.keys())

    def get_all_tools(self) -> dict[str, dict[str, Any]]:
        """Returns the complete tool registry."""
        return self._tools.copy()

    def discover_tools(
        self, pattern: str = "*_tool.py", project_root: Path | None = None
    ) -> list[Path]:
        """
        Uses SovereignIndex to discover tool files matching a pattern.

        Args:
            pattern: Glob pattern for tool files (default: *_tool.py)
            project_root: Optional project root path (defaults to cwd)

        Returns:
            List of discovered tool file paths
        """
        if project_root is None:
            project_root = Path.cwd()
        idx = SovereignIndex.get_instance(project_root)
        return idx.get_files(pattern)

    def auto_register_from_pattern(
        self, pattern: str = "*_tool.py", tool_loader: Callable[[Path], tuple] | None = None
    ) -> int:
        """
        Auto-discovers and registers tools matching a pattern.

        Args:
            pattern: Glob pattern for tool files
            tool_loader: Optional function that takes a Path and returns
                        (tool_name, tool_func, description) tuple

        Returns:
            Number of tools successfully registered
        """
        discovered = self.discover_tools(pattern)
        registered = 0

        for tool_path in discovered:
            if tool_loader:
                try:
                    tool_name, tool_func, description = tool_loader(tool_path)
                    if self.register_tool(tool_name, str(tool_path), tool_func, description):
                        registered += 1
                except Exception as e:
                    Logger.warning(f"[REGISTRY] Failed to load tool from {tool_path}: {e}")
            else:
                # Default: use filename as tool name, placeholder func
                tool_name = tool_path.stem
                if self.register_tool(
                    tool_name, str(tool_path), lambda: None, f"Tool from {tool_path.name}"
                ):
                    registered += 1

        Logger.info(
            f"[REGISTRY] Auto-registered {registered}/{len(discovered)} tools from pattern '{pattern}'"
        )
        return registered

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, tool_name: str) -> bool:
        return tool_name in self._tools
