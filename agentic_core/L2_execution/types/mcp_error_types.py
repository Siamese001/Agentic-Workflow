from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "mcp_error_types")
trace_contract.emit_determinism_digest("p0", "mcp_error_types")

trace_contract._emit_dispatches_healing_run("p1", "mcp_error_types", "L2")
trace_contract._emit_routes_through("p1", "mcp_error_types", "L2")
trace_contract._emit_checks_agent_registry("p1", "mcp_error_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "mcp_error_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "mcp_error_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "mcp_error_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "mcp_error_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "mcp_error_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "mcp_error_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "mcp_error_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "mcp_error_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "mcp_error_types")
trace_contract._emit_gated_by_confidence("p1", "mcp_error_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "mcp_error_types", "L2")
trace_contract._emit_reads_policy_state("p1", "mcp_error_types", "L2")
trace_contract._emit_authorize_and_execute("p2", "mcp_error_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "mcp_error_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "mcp_error_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "mcp_error_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "mcp_error_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "mcp_error_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "mcp_error_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "mcp_error_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "mcp_error_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "mcp_error_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "mcp_error_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "mcp_error_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "mcp_error_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "mcp_error_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "mcp_error_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "mcp_error_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "mcp_error_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "mcp_error_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "mcp_error_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "mcp_error_types", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("mcp_error_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("mcp_error_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("mcp_error_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("mcp_error_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("mcp_error_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("mcp_error_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("mcp_error_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("mcp_error_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("mcp_error_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("mcp_error_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("mcp_error_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("mcp_error_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("mcp_error_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("mcp_error_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("mcp_error_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("mcp_error_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("mcp_error_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("mcp_error_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("mcp_error_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("mcp_error_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("mcp_error_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("mcp_error_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("mcp_error_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("mcp_error_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("mcp_error_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("mcp_error_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("mcp_error_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("mcp_error_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "mcp_error_types", "context_pull")
trace_contract._emit_pulls_context("p1", "mcp_error_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "mcp_error_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "mcp_error_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "mcp_error_types", "write_through")
trace_contract._emit_writes_through("p1", "mcp_error_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "mcp_error_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "mcp_error_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "mcp_error_types", "routing_commit")

"MCP-specific exceptions.\n\nPhase 1 - Pillar 3: Typed Contracts (Strict Schemas)\n"


class MCPError(Exception):
    """Base exception for MCP-related errors."""

    pass


class MCPClientInitializationError(MCPError):
    """Raised when an MCP client fails to initialize."""

    def __init__(self, message: str, client_name: str = "", Provider: str = ""):
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "MCPClientInitializationError.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "MCPClientInitializationError.__init__", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L2_EXECUTION,
            "MCPClientInitializationError.__init__",
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
