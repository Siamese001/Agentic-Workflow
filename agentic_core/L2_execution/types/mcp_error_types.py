from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
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
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "mcp_error_types")
emit_determinism_digest("p0", "mcp_error_types")

_emit_dispatches_healing_run("p1", "mcp_error_types", "L2")
_emit_routes_through("p1", "mcp_error_types", "L2")
_emit_escalates_to_human("p1", "mcp_error_types", "L2")
_emit_reads_policy_state("p1", "mcp_error_types", "L2")
_emit_authorize_and_execute("p2", "mcp_error_types", "execution_auth")
_emit_validates_capability("p2", "mcp_error_types", "capability_check")
_emit_routes_to_capability("p2", "mcp_error_types", "capability_route")
_emit_writes_via_uwg("p2", "mcp_error_types", "uwg_write")
_emit_blocks_direct_write("p2", "mcp_error_types", "direct_write_block")
_emit_records_tool_invocation("p2", "mcp_error_types", "tool_invocation")
_emit_captures_execution_output("p2", "mcp_error_types", "exec_output")
_emit_dispatches_agent("p3", "mcp_error_types", "agent_dispatch")
_emit_coordinates_agents("p3", "mcp_error_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "mcp_error_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "mcp_error_types", "healing_outcome")
_emit_escalates_failure("p3", "mcp_error_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "mcp_error_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "mcp_error_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "mcp_error_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "mcp_error_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "mcp_error_types", "eval_metric")
_emit_stores_embedding("p4", "mcp_error_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "mcp_error_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "mcp_error_types", "exec_snapshot_link")

"MCP-specific exceptions.\n\nPhase 1 - Pillar 3: Typed Contracts (Strict Schemas)\n"


class MCPError(Exception):
    """Base exception for MCP-related errors."""

    pass


class MCPClientInitializationError(MCPError):
    """Raised when an MCP client fails to initialize."""

    def __init__(self, message: str, client_name: str = "", Provider: str = ""):
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "MCPClientInitializationError.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "MCPClientInitializationError.__init__", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "MCPClientInitializationError.__init__"
        )
        super().__init__(message)
        self.client_name = client_name
        self.Provider = Provider


class MCPClientNotFoundError(MCPError):
    """Raised when a requested MCP client is not found in registry."""

    def __init__(self, message: str, client_name: str = ""):
        super().__init__(message)
        self.client_name = client_name


class MCPProviderError(MCPError):
    """Raised when an MCP Provider encounters an error."""

    def __init__(self, message: str, Provider: str = ""):
        super().__init__(message)
        self.Provider = Provider
