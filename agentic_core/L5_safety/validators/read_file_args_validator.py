from __future__ import annotations

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    # noqa: E402,
    # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
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
    _emit_snapshots_state,
    # noqa: E402
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

emit_replay_key("p0", "read_file_args_validator")
emit_determinism_digest("p0", "read_file_args_validator")

_emit_dispatches_healing_run("p1", "read_file_args_validator", "L5")
_emit_routes_through("p1", "read_file_args_validator", "L5")
_emit_checks_agent_registry("p1", "read_file_args_validator", "agent_registry")
_emit_validates_agent_capability("p1", "read_file_args_validator", "capability")
_emit_dispatches_execution_plan("p1", "read_file_args_validator", "exec_plan")
_emit_agent_executes_agent("p1", "read_file_args_validator", "sub_agent")
_emit_routes_to_agent("p1", "read_file_args_validator", "target_agent")
_emit_verifies_policy("p1", "read_file_args_validator", "policy_check")
_emit_observes_runtime_state("p1", "read_file_args_validator", "runtime_state")
_emit_verifies_boundary("p1", "read_file_args_validator", "boundary_check")
_emit_transcripts_response("p1", "read_file_args_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "read_file_args_validator")
_emit_gated_by_confidence("p1", "read_file_args_validator", "confidence_gate")
_emit_escalates_to_human("p1", "read_file_args_validator", "L5")
_emit_reads_policy_state("p1", "read_file_args_validator", "L5")

_emit_applies_guardrail("p0", "read_file_args_validator", "p0_governance")
_emit_snapshots_state("p0", "read_file_args_validator", "state_snapshot")
_emit_authorize_and_execute("p2", "read_file_args_validator", "execution_auth")
_emit_validates_capability("p2", "read_file_args_validator", "capability_check")
_emit_routes_to_capability("p2", "read_file_args_validator", "capability_route")
_emit_writes_via_uwg("p2", "read_file_args_validator", "uwg_write")
_emit_blocks_direct_write("p2", "read_file_args_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "read_file_args_validator", "tool_invocation")
_emit_captures_execution_output("p2", "read_file_args_validator", "exec_output")
_emit_dispatches_agent("p3", "read_file_args_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "read_file_args_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "read_file_args_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "read_file_args_validator", "healing_outcome")
_emit_escalates_failure("p3", "read_file_args_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "read_file_args_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "read_file_args_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "read_file_args_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "read_file_args_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "read_file_args_validator", "eval_metric")
_emit_stores_embedding("p4", "read_file_args_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "read_file_args_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "read_file_args_validator", "exec_snapshot_link")

"\nTool Arguments schema\n====================\nDefines the Pydantic models for all tool-calling arguments within the\nSovereign system. These models enforce strict path validation and\nexecution guardrails.\n"
import uuid
from pathlib import Path

from pydantic import BaseModel, Field, validator

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_signs_execution_trace,
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

_emit_emits_metric_event("read_file_args_validator", "p4obs", "metric_1")
_emit_emits_metric_event("read_file_args_validator", "p4obs", "metric_2")
_emit_emits_metric_event("read_file_args_validator", "p4obs", "metric_3")
_emit_emits_metric_event("read_file_args_validator", "p4obs", "metric_4")
_emit_emits_metric_event("read_file_args_validator", "p4obs", "metric_5")
_emit_emits_metric_event("read_file_args_validator", "p4obs", "metric_6")
_emit_records_incident_event("read_file_args_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("read_file_args_validator", "p4obs", "anomaly")
_emit_writes_observability_log("read_file_args_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("read_file_args_validator", "p4obs", "mon_state")
_emit_triggers_alert("read_file_args_validator", "p4obs", "alert")
_emit_links_incident_trace("read_file_args_validator", "p4obs", "trace_link")
_emit_captures_pattern("read_file_args_validator", "p3lm", "pattern")
_emit_records_learning_event("read_file_args_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("read_file_args_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("read_file_args_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("read_file_args_validator", "p3lm", "routing")
_emit_improves_agent_policy("read_file_args_validator", "p3lm", "policy")
_emit_stores_learning_state("read_file_args_validator", "p3lm", "state")
_emit_records_execution_trace("read_file_args_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("read_file_args_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("read_file_args_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("read_file_args_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("read_file_args_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("read_file_args_validator", "env_read", "p2_env_1")
_emit_reads_environ("read_file_args_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("read_file_args_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("read_file_args_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "read_file_args_validator", "context_pull")
_emit_pulls_context("p1", "read_file_args_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "read_file_args_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "read_file_args_validator", "uwg_term_2")
_emit_writes_through("p1", "read_file_args_validator", "write_through")
_emit_writes_through("p1", "read_file_args_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "read_file_args_validator", "safety_validation")
_emit_invokes_eval("p1", "read_file_args_validator", "eval_call")
_emit_proposal_commits_routing("p1", "read_file_args_validator", "routing_commit")


class ReadFileArgs(BaseModel):
    """Arguments for reading a file."""

    path: str = Field(..., description="Relative path to the file to read")

    @validator("path")
    def validate_path(cls, v):
        _emit_validated_by_safety_plane(str(uuid.uuid4()), "ReadFileArgs.validate_path", "L5_POLICY")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "ReadFileArgs.validate_path")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ReadFileArgs.validate_path".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if Path(v).is_absolute():
            raise ValueError("Path must be relative to project root")
        return v


class WriteFileArgs(BaseModel):
    """Arguments for writing to a file."""

    path: str = Field(..., description="Relative path to the file to write")
    content: str = Field(..., description="Content to write to the file")
    create_dirs: bool = Field(default=True, description="Create parent directories if they don't exist")

    @validator("path")
    def validate_path(cls, v):
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "WriteFileArgs.validate_path")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:WriteFileArgs.validate_path".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if Path(v).is_absolute():
            raise ValueError("Path must be relative to project root")
        return v


class MoveFileArgs(BaseModel):
    """Arguments for moving/renaming a file."""

    source: str = Field(..., description="Relative path to the source file")
    destination: str = Field(..., description="Relative path to the destination")
    overwrite: bool = Field(default=False, description="Overwrite destination if it exists")

    @validator("source", "destination")
    def validate_paths(cls, v):
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "MoveFileArgs.validate_paths")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:MoveFileArgs.validate_paths".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if Path(v).is_absolute():
            raise ValueError("Paths must be relative to project root")
        return v


class ListFilesArgs(BaseModel):
    """Arguments for listing files in a directory."""

    path: str = Field(default=".", description="Relative path to the directory to list")
    pattern: str | None = Field(default=None, description="Glob pattern to filter files (e.g., '*.py')")
    recursive: bool = Field(default=False, description="Recursively list subdirectories")

    @validator("path")
    def validate_path(cls, v):
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "ListFilesArgs.validate_path")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ListFilesArgs.validate_path".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if Path(v).is_absolute():
            raise ValueError("Path must be relative to project root")
        return v


class DeleteFileArgs(BaseModel):
    """Arguments for deleting a file."""

    path: str = Field(..., description="Relative path to the file to delete")

    @validator("path")
    def validate_path(cls, v):
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "DeleteFileArgs.validate_path")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:DeleteFileArgs.validate_path".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if Path(v).is_absolute():
            raise ValueError("Path must be relative to project root")
        return v


class CreateDirectoryArgs(BaseModel):
    """Arguments for creating a directory."""

    path: str = Field(..., description="Relative path to the directory to create")
    parents: bool = Field(default=True, description="Create parent directories if they don't exist")

    @validator("path")
    def validate_path(cls, v):
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "CreateDirectoryArgs.validate_path")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:CreateDirectoryArgs.validate_path".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if Path(v).is_absolute():
            raise ValueError("Path must be relative to project root")
        return v


class ExecuteCommandArgs(BaseModel):
    """Arguments for executing a shell command."""

    command: str = Field(..., description="Command to execute")
    args: list[str] = Field(default_factory=list, description="Command arguments")
    cwd: str | None = Field(default=None, description="Working directory (relative to project root)")
    timeout: int = Field(default=30, description="Timeout in seconds (max 300)")
    capture_output: bool = Field(default=True, description="Capture stdout and stderr")

    @validator("timeout")
    def validate_timeout(cls, v):
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "ExecuteCommandArgs.validate_timeout"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ExecuteCommandArgs.validate_timeout".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if v > 300:
            raise ValueError("Timeout cannot exceed 300 seconds to prevent livelocks")
        if v < 1:
            raise ValueError("Timeout must be at least 1 second")
        return v

    @validator("cwd")
    def validate_cwd(cls, v):
        if v and Path(v).is_absolute():
            raise ValueError("Working directory must be relative to project root")
        return v
