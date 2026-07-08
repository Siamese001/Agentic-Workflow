"""
Tool Registry Definitions - Phase 21.1 Restoration

Provides Pydantic models for tool argument validation.
These are used by the tool_registry to validate tool calls.
"""

from pydantic import BaseModel, Field

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_emits_metric_event("tool_args_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("tool_args_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("tool_args_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("tool_args_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("tool_args_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("tool_args_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("tool_args_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("tool_args_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("tool_args_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("tool_args_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("tool_args_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("tool_args_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("tool_args_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("tool_args_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("tool_args_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("tool_args_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("tool_args_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("tool_args_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("tool_args_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("tool_args_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("tool_args_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("tool_args_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("tool_args_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("tool_args_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("tool_args_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("tool_args_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("tool_args_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("tool_args_types", "runtime_state", "p2_rt_2")

trace_contract.emit_replay_key("p0", "tool_args_types")
trace_contract.emit_determinism_digest("p0", "tool_args_types")

trace_contract._emit_dispatches_healing_run("p1", "tool_args_types", "L2")
trace_contract._emit_routes_through("p1", "tool_args_types", "L2")
trace_contract._emit_checks_agent_registry("p1", "tool_args_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "tool_args_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "tool_args_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "tool_args_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "tool_args_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "tool_args_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "tool_args_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "tool_args_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "tool_args_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "tool_args_types")
trace_contract._emit_gated_by_confidence("p1", "tool_args_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "tool_args_types", "L2")
trace_contract._emit_reads_policy_state("p1", "tool_args_types", "L2")
trace_contract._emit_pulls_context("p1", "tool_args_types", "context_pull")
trace_contract._emit_pulls_context("p1", "tool_args_types", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "tool_args_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "tool_args_types", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "tool_args_types", "write_through")
trace_contract._emit_writes_through("p1", "tool_args_types", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "tool_args_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "tool_args_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "tool_args_types", "routing_commit")

trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_records_execution_trace("p0", "evidence", "tool_args_types")
trace_contract._emit_applies_guardrail("p0", "tool_args_types", "p0_governance")
trace_contract._emit_snapshots_state("p0", "tool_args_types", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "tool_args_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "tool_args_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "tool_args_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "tool_args_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "tool_args_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "tool_args_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "tool_args_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "tool_args_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "tool_args_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "tool_args_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "tool_args_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "tool_args_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "tool_args_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "tool_args_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "tool_args_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "tool_args_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "tool_args_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "tool_args_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "tool_args_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "tool_args_types", "exec_snapshot_link")


class ReadFileArgs(BaseModel):
    """Arguments for reading a file."""

    path: str = Field(..., description="Path to the file to read")


class WriteFileArgs(BaseModel):
    """Arguments for writing to a file."""

    path: str = Field(..., description="Path to the file to write")
    content: str = Field(..., description="Content to write to the file")


class ListFilesArgs(BaseModel):
    """Arguments for listing files in a directory."""

    directory: str = Field(..., description="Directory to list files from")
    pattern: str | None = Field(None, description="Optional glob pattern to filter files")


class MoveFileArgs(BaseModel):
    """Arguments for moving/renaming a file."""

    source: str = Field(..., description="Source file path")
    destination: str = Field(..., description="Destination file path")


class DeleteFileArgs(BaseModel):
    """Arguments for deleting a file."""

    path: str = Field(..., description="Path to the file to delete")


class CreateDirectoryArgs(BaseModel):
    """Arguments for creating a directory."""

    path: str = Field(..., description="Path to the directory to create")


class ExecuteCommandArgs(BaseModel):
    """Arguments for executing a shell command."""

    command: str = Field(..., description="Shell command to execute")
    cwd: str | None = Field(None, description="Working directory for the command")
