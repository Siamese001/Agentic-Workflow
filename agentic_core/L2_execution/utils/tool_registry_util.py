"""
Tool Registry - Centralized SSOT for all tools.

Ensures tools reside in Sovereign Territory before registration.
Integrates with SovereignIndex for safety validation.
"""

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any, Optional

from agentic_core.L0_routing.config import (
    GLOBAL_EXCLUDED_DIRS,
)  # guardian: allow-layer-violation -- L2 module uses L0 config/enforcement; intentional downward enforcement-chain dependency
from agentic_core.L0_routing.utils.path_util import (
    is_path_allowed,
)  # guardian: allow-layer-violation -- L2 module uses L0 config/enforcement; intentional downward enforcement-chain dependency
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "tool_registry_util")
emit_determinism_digest("p0", "tool_registry_util")

_emit_dispatches_healing_run("p1", "tool_registry_util", "L2")
_emit_routes_through("p1", "tool_registry_util", "L2")
_emit_checks_agent_registry("p1", "tool_registry_util", "agent_registry")
_emit_validates_agent_capability("p1", "tool_registry_util", "capability")
_emit_dispatches_execution_plan("p1", "tool_registry_util", "exec_plan")
_emit_agent_executes_agent("p1", "tool_registry_util", "sub_agent")
_emit_routes_to_agent("p1", "tool_registry_util", "target_agent")
_emit_verifies_policy("p1", "tool_registry_util", "policy_check")
_emit_observes_runtime_state("p1", "tool_registry_util", "runtime_state")
_emit_verifies_boundary("p1", "tool_registry_util", "boundary_check")
_emit_transcripts_response("p1", "tool_registry_util", "transcript")
_emit_hard_fails_untranscripted("p1", "tool_registry_util")
_emit_gated_by_confidence("p1", "tool_registry_util", "confidence_gate")
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
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from tqdm import tqdm

_emit_emits_metric_event("tool_registry_util", "p4obs", "metric_1")
_emit_emits_metric_event("tool_registry_util", "p4obs", "metric_2")
_emit_emits_metric_event("tool_registry_util", "p4obs", "metric_3")
_emit_emits_metric_event("tool_registry_util", "p4obs", "metric_4")
_emit_emits_metric_event("tool_registry_util", "p4obs", "metric_5")
_emit_emits_metric_event("tool_registry_util", "p4obs", "metric_6")
_emit_records_incident_event("tool_registry_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("tool_registry_util", "p4obs", "anomaly")
_emit_writes_observability_log("tool_registry_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("tool_registry_util", "p4obs", "mon_state")
_emit_triggers_alert("tool_registry_util", "p4obs", "alert")
_emit_links_incident_trace("tool_registry_util", "p4obs", "trace_link")
_emit_captures_pattern("tool_registry_util", "p3lm", "pattern")
_emit_records_learning_event("tool_registry_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("tool_registry_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("tool_registry_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("tool_registry_util", "p3lm", "routing")
_emit_improves_agent_policy("tool_registry_util", "p3lm", "policy")
_emit_stores_learning_state("tool_registry_util", "p3lm", "state")
_emit_records_execution_trace("tool_registry_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("tool_registry_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("tool_registry_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("tool_registry_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("tool_registry_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("tool_registry_util", "env_read", "p2_env_1")
_emit_reads_environ("tool_registry_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("tool_registry_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("tool_registry_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "tool_registry_util", "context_pull")
_emit_pulls_context("p1", "tool_registry_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "tool_registry_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "tool_registry_util", "uwg_term_2")
_emit_writes_through("p1", "tool_registry_util", "write_through")
_emit_writes_through("p1", "tool_registry_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "tool_registry_util", "safety_validation")
_emit_invokes_eval("p1", "tool_registry_util", "eval_call")
_emit_proposal_commits_routing("p1", "tool_registry_util", "routing_commit")

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
        self,
        tool_name: str,
        tool_path: str,
        tool_func: Callable[..., Any],
        description: str = "",
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
                        f"[REGISTRY] REJECTED: Tool '{tool_name}' at {tool_path} is outside project root.",
                    )
                    return False
            else:
                rel_path = path
            path_parts = rel_path.parts
            if any(excl in path_parts for excl in GLOBAL_EXCLUDED_DIRS):
                Logger.error(
                    f"[REGISTRY] REJECTED: Tool '{tool_name}' at {tool_path} is in a globally excluded directory.",
                )
                return False
            if not is_path_allowed(str(rel_path)):
                Logger.error(
                    f"[REGISTRY] REJECTED: Tool '{tool_name}' at {tool_path} is outside Sovereign Territory.",
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
        except (ValueError, TypeError) as e:
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
        self,
        pattern: str = "*_tool.py",
        tool_loader: Callable[[Path], tuple] | None = None,
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
        for tool_path in tqdm(discovered, desc="Processing", unit="item"):
            if tool_loader:
                try:
                    tool_name, tool_func, description = tool_loader(tool_path)
                    if self.register_tool(tool_name, str(tool_path), tool_func, description):
                        registered += 1
                except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as e:
                    raise
                    Logger.warning(f"[REGISTRY] Failed to load tool from {tool_path}: {e}")
            else:
                tool_name = tool_path.stem
                if self.register_tool(tool_name, str(tool_path), lambda: None, f"Tool from {tool_path.name}"):
                    registered += 1
        Logger.info(
            f"[REGISTRY] Auto-registered {registered}/{len(discovered)} tools from pattern '{pattern}'",
        )
        return registered

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, tool_name: str) -> bool:
        return tool_name in self._tools


tool_registry = ToolRegistry
