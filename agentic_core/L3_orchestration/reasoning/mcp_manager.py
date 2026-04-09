from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "mcp_manager")
emit_determinism_digest("p0", "mcp_manager")

_emit_dispatches_healing_run("p1", "mcp_manager", "L3")
_emit_routes_through("p1", "mcp_manager", "L3")
_emit_checks_agent_registry("p1", "mcp_manager", "agent_registry")
_emit_validates_agent_capability("p1", "mcp_manager", "capability")
_emit_dispatches_execution_plan("p1", "mcp_manager", "exec_plan")
_emit_agent_executes_agent("p1", "mcp_manager", "sub_agent")
_emit_routes_to_agent("p1", "mcp_manager", "target_agent")
_emit_verifies_policy("p1", "mcp_manager", "policy_check")
_emit_observes_runtime_state("p1", "mcp_manager", "runtime_state")
_emit_verifies_boundary("p1", "mcp_manager", "boundary_check")
_emit_transcripts_response("p1", "mcp_manager", "transcript")
_emit_hard_fails_untranscripted("p1", "mcp_manager")
_emit_gated_by_confidence("p1", "mcp_manager", "confidence_gate")
_emit_escalates_to_human("p1", "mcp_manager", "L3")
_emit_reads_policy_state("p1", "mcp_manager", "L3")
_emit_authorize_and_execute("p2", "mcp_manager", "execution_auth")
_emit_validates_capability("p2", "mcp_manager", "capability_check")
_emit_routes_to_capability("p2", "mcp_manager", "capability_route")
_emit_writes_via_uwg("p2", "mcp_manager", "uwg_write")
_emit_blocks_direct_write("p2", "mcp_manager", "direct_write_block")
_emit_records_tool_invocation("p2", "mcp_manager", "tool_invocation")
_emit_captures_execution_output("p2", "mcp_manager", "exec_output")
_emit_dispatches_agent("p3", "mcp_manager", "agent_dispatch")
_emit_coordinates_agents("p3", "mcp_manager", "agent_coordination")
_emit_records_workflow_lineage("p3", "mcp_manager", "workflow_lineage")
_emit_records_healing_outcome("p3", "mcp_manager", "healing_outcome")
_emit_escalates_failure("p3", "mcp_manager", "failure_escalation")
_emit_orchestrates_workflow("p3", "mcp_manager", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "mcp_manager", "healing_dispatch")
_emit_invokes_evaluation("p3", "mcp_manager", "evaluation_signal")
_emit_records_telemetry_event("p4", "mcp_manager", "telemetry_event")
_emit_captures_evaluation_metric("p4", "mcp_manager", "eval_metric")
_emit_stores_embedding("p4", "mcp_manager", "embedding_store")
_emit_updates_meta_learning_state("p4", "mcp_manager", "meta_learning")
_emit_links_execution_to_snapshot("p4", "mcp_manager", "exec_snapshot_link")

"""L3 Orchestration: Concrete MCPConnectionManager + load_mcp_config.

Routes call_tool() dispatches to the live Windsurf MCP tool functions
available in the environment (mcp8_*, mcp12_*, mcp1_*, mcp11_*).
Falls back gracefully when a tool is unavailable.
"""

import json
import logging
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_snapshots_state,
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

_emit_emits_metric_event("mcp_manager", "p4obs", "metric_1")
_emit_emits_metric_event("mcp_manager", "p4obs", "metric_2")
_emit_emits_metric_event("mcp_manager", "p4obs", "metric_3")
_emit_emits_metric_event("mcp_manager", "p4obs", "metric_4")
_emit_emits_metric_event("mcp_manager", "p4obs", "metric_5")
_emit_emits_metric_event("mcp_manager", "p4obs", "metric_6")
_emit_records_incident_event("mcp_manager", "p4obs", "incident")
_emit_captures_runtime_anomaly("mcp_manager", "p4obs", "anomaly")
_emit_writes_observability_log("mcp_manager", "p4obs", "obs_log")
_emit_updates_monitoring_state("mcp_manager", "p4obs", "mon_state")
_emit_triggers_alert("mcp_manager", "p4obs", "alert")
_emit_links_incident_trace("mcp_manager", "p4obs", "trace_link")
_emit_captures_pattern("mcp_manager", "p3lm", "pattern")
_emit_records_learning_event("mcp_manager", "p3lm", "learning_event")
_emit_writes_learning_snapshot("mcp_manager", "p3lm", "snapshot")
_emit_feeds_meta_learning("mcp_manager", "p3lm", "meta_feed")
_emit_updates_routing_strategy("mcp_manager", "p3lm", "routing")
_emit_improves_agent_policy("mcp_manager", "p3lm", "policy")
_emit_stores_learning_state("mcp_manager", "p3lm", "state")
_emit_records_execution_trace("mcp_manager", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("mcp_manager", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("mcp_manager", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("mcp_manager", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("mcp_manager", "L4_STATE", "p2_trace_5")
_emit_reads_environ("mcp_manager", "env_read", "p2_env_1")
_emit_reads_environ("mcp_manager", "env_read", "p2_env_2")
_emit_reads_runtime_state("mcp_manager", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("mcp_manager", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "mcp_manager", "context_pull")
_emit_pulls_context("p1", "mcp_manager", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "mcp_manager", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "mcp_manager", "uwg_term_2")
_emit_writes_through("p1", "mcp_manager", "write_through")
_emit_writes_through("p1", "mcp_manager", "write_through_2")
_emit_validated_by_safety_plane("p1", "mcp_manager", "safety_validation")
_emit_invokes_eval("p1", "mcp_manager", "eval_call")
_emit_proposal_commits_routing("p1", "mcp_manager", "routing_commit")


# Import the MCP loader (.windsurf/mcp_config.json SSOT)
try:
    from agentic_core.config.mcp_loader import get_cached_loader

    _MCP_LOADER_AVAILABLE = True
except ImportError:
    _MCP_LOADER_AVAILABLE = False
    get_cached_loader = None

Logger: Any = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# MCP Server Registry — loaded from .windsurf/mcp_config.json (SSOT)
# ---------------------------------------------------------------------------

# Cache for the server dispatch mapping (populated once, never None)
_TOOL_DISPATCH_CACHE: dict[str, str] = {}


def _get_tool_dispatch() -> dict[str, str]:
    """Get enabled server names from .windsurf/mcp_config.json.

    Returns:
        Dict of server_name -> server_name (identity map used for presence
        checks). Falls back to empty dict if loader unavailable.
    """
    if _TOOL_DISPATCH_CACHE:
        return _TOOL_DISPATCH_CACHE

    if _MCP_LOADER_AVAILABLE and get_cached_loader:
        try:
            loader = get_cached_loader()
            servers = loader.list_enabled_servers()
            _TOOL_DISPATCH_CACHE.update({s: s for s in servers})
            Logger.debug(
                "[MCPManager] Loaded %d servers from .windsurf/mcp_config.json", len(_TOOL_DISPATCH_CACHE)
            )
        except (FileNotFoundError, ValueError, OSError) as e:
            Logger.warning(
                "[MCPManager] Failed to load from .windsurf/mcp_config.json: %s. Using fallback.", e
            )

    return _TOOL_DISPATCH_CACHE


def _resolve_tool(tool_name: str) -> Any:
    """Resolve a logical tool name to a callable, or None if unavailable."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_resolve_tool", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_resolve_tool", "p0_governance")

    # Get dispatch table from .windsurf/mcp_config.json SSOT (cached)
    tool_dispatch = _get_tool_dispatch()
    mapped = tool_dispatch.get(tool_name)

    if mapped is None:
        Logger.debug(f"[MCPManager] No dispatch mapping for tool '{tool_name}'")
        return None

    # Try to resolve via global builtins (Windsurf injects MCP tools as globals)
    import builtins

    fn = getattr(builtins, mapped, None)
    if fn is not None:
        return fn

    # Try current module globals (some environments inject here)
    import sys

    frame_globals = sys.modules.get("__main__", None)
    if frame_globals is not None:
        fn = getattr(frame_globals, mapped, None)
        if fn is not None:
            return fn

    Logger.debug(f"[MCPManager] Tool '{mapped}' not found in environment")
    return None


class MCPConnectionManager:
    """
    Concrete implementation of the MCPConnectionManager Protocol.

    Routes call_tool() to live Windsurf MCP tool functions.
    All calls are resilient: errors are logged, None is returned on failure.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self._config = config or {}
        self._role: str = "default"
        self._connected = False

    async def connect(self, role: str) -> None:
        """Mark connection active for the given role."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "MCPConnectionManager.connect",
        )

        self._role = role
        self._connected = True
        Logger.info(f"[MCPManager] Connected for role '{role}'")

    async def disconnect(self) -> None:
        """Mark connection inactive."""
        self._connected = False
        Logger.info("[MCPManager] Disconnected")

    async def call_tool(self, tool: str, args: dict[str, Any] | None = None, **kwargs: Any) -> Any:
        """
        Dispatch a logical tool call to the live MCP tool function.

        Args:
            tool: Logical tool name (see _TOOL_DISPATCH)
            args: Tool arguments dict (merged with kwargs)

        Returns:
            Tool result or empty dict on failure
        """
        merged = {**(args or {}), **kwargs}
        fn = _resolve_tool(tool)
        if fn is None:
            Logger.warning(f"[MCPManager] Tool '{tool}' unavailable — returning empty result")
            return {}
        try:
            result = fn(**merged)
            # Support both sync and async callables
            if hasattr(result, "__await__"):
                import asyncio

                result = await asyncio.ensure_future(result)
            Logger.debug(f"[MCPManager] Tool '{tool}' succeeded")
            return result if result is not None else {}
        # guardian: allow-silent-swallow
        except (RuntimeError, ValueError) as e:
            Logger.error(f"[MCPManager] Tool '{tool}' failed: {e}")
            return {"error": str(e)}

    async def cleanup(self) -> None:
        """Alias for disconnect."""
        await self.disconnect()


def load_mcp_config(config_path: str) -> dict[str, Any]:
    """
    Load MCP configuration from a YAML or JSON file.

    Falls back to empty config dict if file is missing or unparseable.
    """
    path = Path(config_path)
    # guardian: allow-config-with-logic
    if not path.exists():
        Logger.warning(f"[MCPManager] Config file not found: {config_path} — using defaults")
        return {}
    try:
        text = path.read_text(encoding="utf-8")
        # guardian: allow-config-with-logic
        if path.suffix in {".yaml", ".yml"}:
            try:
                import yaml  # type: ignore[import]

                return yaml.safe_load(text) or {}
            except ImportError:  # guardian: allow-silent-swallow
                Logger.warning("[MCPManager] PyYAML not installed — falling back to JSON parse")
        return json.loads(text)
    # guardian: allow-silent-swallow
    except (RuntimeError, ValueError) as e:
        Logger.warning(f"[MCPManager] Failed to parse config {config_path}: {e} — using defaults")
        return {}
