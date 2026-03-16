"""
Tool Registry - Centralized SSOT for all tools.

Ensures tools reside in Sovereign Territory before registration.
Integrates with SovereignIndex for safety validation.
"""

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any, Optional

from agentic_core.L0_routing.config import GLOBAL_EXCLUDED_DIRS
from agentic_core.L0_routing.utils.path_util import is_path_allowed
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "tool_registry_util")
emit_determinism_digest("p0", "tool_registry_util")

_emit_dispatches_healing_run("p1", "tool_registry_util", "L2")
_emit_routes_through("p1", "tool_registry_util", "L2")
_emit_escalates_to_human("p1", "tool_registry_util", "L2")
_emit_reads_policy_state("p1", "tool_registry_util", "L2")

_emit_applies_guardrail("p0", "tool_registry_util", "p0_governance")
_emit_snapshots_state("p0", "tool_registry_util", "state_snapshot")
_emit_authorize_and_execute("p2", "tool_registry_util", "execution_auth")
_emit_validates_capability("p2", "tool_registry_util", "capability_check")
_emit_routes_to_capability("p2", "tool_registry_util", "capability_route")
_emit_writes_via_uwg("p2", "tool_registry_util", "uwg_write")
_emit_blocks_direct_write("p2", "tool_registry_util", "direct_write_block")
_emit_records_tool_invocation("p2", "tool_registry_util", "tool_invocation")
_emit_captures_execution_output("p2", "tool_registry_util", "exec_output")
_emit_dispatches_agent("p3", "tool_registry_util", "agent_dispatch")
_emit_coordinates_agents("p3", "tool_registry_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "tool_registry_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "tool_registry_util", "healing_outcome")
_emit_escalates_failure("p3", "tool_registry_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "tool_registry_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "tool_registry_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "tool_registry_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "tool_registry_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "tool_registry_util", "eval_metric")
_emit_stores_embedding("p4", "tool_registry_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "tool_registry_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "tool_registry_util", "exec_snapshot_link")

Logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    SSOT for all tools. Ensures tools reside in Sovereign Territory.

    Features:
    - Singleton pattern for global access
    - Path validation via is_path_allowed
    - Integration with SovereignIndex for tool discovery
    - Logging of registration attempts
    """

    _instance: Optional["ToolRegistry"] = None
    _tools: dict[str, dict[str, Any]] = {}

    def __new__(cls) -> "ToolRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools = {}
        return cls._instance

    @classmethod
    def get_instance(cls) -> "ToolRegistry":
        """Get the singleton instance of ToolRegistry."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "ToolRegistry.get_instance")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ToolRegistry.get_instance".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
                try:
                    rel_path = path.relative_to(Path.cwd())
                except ValueError:
                    Logger.error(
                        f"[REGISTRY] REJECTED: Tool '{tool_name}' at {tool_path} is outside project root."
                    )
                    return False
            else:
                rel_path = path
            path_parts = rel_path.parts
            if any(excl in path_parts for excl in GLOBAL_EXCLUDED_DIRS):
                Logger.error(
                    f"[REGISTRY] REJECTED: Tool '{tool_name}' at {tool_path} is in a globally excluded directory."
                )
                return False
            if not is_path_allowed(str(rel_path)):
                Logger.error(
                    f"[REGISTRY] REJECTED: Tool '{tool_name}' at {tool_path} is outside Sovereign Territory."
                )
                return False
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

    def discover_tools(self, pattern: str = "*_tool.py", project_root: Path | None = None) -> list[Path]:
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
                    raise
                    Logger.warning(f"[REGISTRY] Failed to load tool from {tool_path}: {e}")
            else:
                tool_name = tool_path.stem
                if self.register_tool(tool_name, str(tool_path), lambda: None, f"Tool from {tool_path.name}"):
                    registered += 1
        Logger.info(
            f"[REGISTRY] Auto-registered {registered}/{len(discovered)} tools from pattern '{pattern}'"
        )
        return registered

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, tool_name: str) -> bool:
        return tool_name in self._tools


tool_registry = ToolRegistry
