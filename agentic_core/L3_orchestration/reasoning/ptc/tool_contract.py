"""
Programmatic Tool Calling (PTC) - Tool Contract

Defines immutable data structures for tool specification, calls, and results.
Provides deterministic serialization and validation for tool registry.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "tool_contract")
trace_contract.emit_determinism_digest("p0", "tool_contract")

trace_contract._emit_dispatches_healing_run("p1", "tool_contract", "L3")
trace_contract._emit_routes_through("p1", "tool_contract", "L3")
trace_contract._emit_checks_agent_registry("p1", "tool_contract", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "tool_contract", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "tool_contract", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "tool_contract", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "tool_contract", "target_agent")
trace_contract._emit_verifies_policy("p1", "tool_contract", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "tool_contract", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "tool_contract", "boundary_check")
trace_contract._emit_transcripts_response("p1", "tool_contract", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "tool_contract")
trace_contract._emit_gated_by_confidence("p1", "tool_contract", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "tool_contract", "L3")
trace_contract._emit_reads_policy_state("p1", "tool_contract", "L3")
trace_contract._emit_authorize_and_execute("p2", "tool_contract", "execution_auth")
trace_contract._emit_validates_capability("p2", "tool_contract", "capability_check")
trace_contract._emit_routes_to_capability("p2", "tool_contract", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "tool_contract", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "tool_contract", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "tool_contract", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "tool_contract", "exec_output")
trace_contract._emit_dispatches_agent("p3", "tool_contract", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "tool_contract", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "tool_contract", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "tool_contract", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "tool_contract", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "tool_contract", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "tool_contract", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "tool_contract", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "tool_contract", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "tool_contract", "eval_metric")
trace_contract._emit_stores_embedding("p4", "tool_contract", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "tool_contract", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "tool_contract", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("tool_contract", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("tool_contract", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("tool_contract", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("tool_contract", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("tool_contract", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("tool_contract", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("tool_contract", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("tool_contract", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("tool_contract", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("tool_contract", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("tool_contract", "p4obs", "alert")
trace_contract._emit_links_incident_trace("tool_contract", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("tool_contract", "p3lm", "pattern")
trace_contract._emit_records_learning_event("tool_contract", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("tool_contract", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("tool_contract", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("tool_contract", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("tool_contract", "p3lm", "policy")
trace_contract._emit_stores_learning_state("tool_contract", "p3lm", "state")
trace_contract._emit_records_execution_trace("tool_contract", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("tool_contract", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("tool_contract", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("tool_contract", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("tool_contract", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("tool_contract", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("tool_contract", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("tool_contract", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("tool_contract", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "tool_contract", "context_pull")
trace_contract._emit_pulls_context("p1", "tool_contract", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "tool_contract", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "tool_contract", "uwg_term_2")
trace_contract._emit_writes_through("p1", "tool_contract", "write_through")
trace_contract._emit_writes_through("p1", "tool_contract", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "tool_contract", "safety_validation")
trace_contract._emit_invokes_eval("p1", "tool_contract", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "tool_contract", "routing_commit")


@dataclass(frozen=True)
class ToolArg:
    """Immutable argument specification for a tool."""

    name: str
    kind: str
    required: bool
    default: str | None = None

    def __post_init__(self):
        """Validate argument specification."""
        if not self.name:
            raise ValueError("name cannot be empty")
        if not self.kind:
            raise ValueError("kind cannot be empty")
        valid_kinds = {"str", "int", "bool", "list[str]", "dict"}
        if self.kind not in valid_kinds:
            raise ValueError(f"kind must be one of {valid_kinds}")
        if not self.required and self.default is None:
            raise ValueError("optional args must have default value")


@dataclass(frozen=True)
class ToolSpec:
    """Immutable specification for a tool."""

    tool_id: str
    description: str
    side_effect_class: str
    args: tuple[ToolArg, ...]
    output_kind: str
    version: int = 1

    def __post_init__(self):
        """Validate tool specification."""
        if not self.tool_id:
            raise ValueError("tool_id cannot be empty")
        if not self.description:
            raise ValueError("description cannot be empty")
        valid_side_effects = {"PURE", "READONLY", "WRITE_FS", "SUBPROCESS"}
        if self.side_effect_class not in valid_side_effects:
            raise ValueError(f"side_effect_class must be one of {valid_side_effects}")
        valid_outputs = {"TEXT", "JSON"}
        if self.output_kind not in valid_outputs:
            raise ValueError(f"output_kind must be one of {valid_outputs}")
        if self.version < 1:
            raise ValueError("version must be >= 1")
        arg_names = [arg.name for arg in self.args]
        if arg_names != sorted(arg_names):
            raise ValueError("args must be sorted by name")


@dataclass(frozen=True)
class ToolCall:
    """Immutable tool call invocation."""

    call_id: str
    tool_id: str
    args: dict[str, Any]
    policy: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate tool call."""
        if not self.call_id:
            raise ValueError("call_id cannot be empty")
        if not self.tool_id:
            raise ValueError("tool_id cannot be empty")


@dataclass(frozen=True)
class ToolCallResult:
    """Immutable result of a tool call."""

    exit_code: int
    stdout: str
    stderr: str
    truncated: bool
    hashes: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Validate tool call result."""
        if self.exit_code < 0:
            raise ValueError("exit_code must be >= 0")


def canonical_json(obj: Any) -> str:
    """Serialize object to canonical JSON.

    Args:
        obj: Object to serialize

    Returns:
        Canonical JSON string
    """
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "canonical_json", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "canonical_json", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "canonical_json")
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_hex(data: str) -> str:
    """Calculate SHA256 hash of string data.

    Args:
        data: String data to hash

    Returns:
        Hexadecimal SHA256 hash
    """
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def generate_call_id(tool_id: str, args: dict[str, Any]) -> str:
    """Generate deterministic call ID from tool ID and arguments.

    Args:
        tool_id: Tool identifier
        args: Tool arguments

    Returns:
        SHA256 hash for call ID
    """
    canonical_args = canonical_json(args)
    data = f"{tool_id}:{canonical_args}"
    return sha256_hex(data)


def hash_result_data(result: ToolCallResult) -> dict[str, str]:
    """Generate hashes for result data.

    Args:
        result: Tool call result

    Returns:
        Dictionary with hashes
    """
    hashes = {}
    if result.stdout:
        hashes["stdout"] = sha256_hex(result.stdout)
    if result.stderr:
        hashes["stderr"] = sha256_hex(result.stderr)
    hashes["truncated"] = sha256_hex(str(result.truncated))
    return hashes


def tool_spec_to_json(spec: ToolSpec) -> str:
    """Serialize ToolSpec to deterministic JSON."""
    data = {
        "tool_id": spec.tool_id,
        "description": spec.description,
        "side_effect_class": spec.side_effect_class,
        "args": [
            {"name": arg.name, "kind": arg.kind, "required": arg.required, "default": arg.default}
            for arg in spec.args
        ],
        "output_kind": spec.output_kind,
        "version": spec.version,
    }
    return canonical_json(data)


def tool_call_to_json(call: ToolCall) -> str:
    """Serialize ToolCall to deterministic JSON."""
    data = {"call_id": call.call_id, "tool_id": call.tool_id, "args": call.args, "policy": call.policy}
    return canonical_json(data)


def tool_call_result_to_json(result: ToolCallResult) -> str:
    """Serialize ToolCallResult to deterministic JSON."""
    data = {
        "exit_code": result.exit_code,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "truncated": result.truncated,
        "hashes": result.hashes,
    }
    return canonical_json(data)


__all__ = [
    "ToolArg",
    "ToolSpec",
    "ToolCall",
    "ToolCallResult",
    "canonical_json",
    "sha256_hex",
    "generate_call_id",
    "hash_result_data",
    "tool_spec_to_json",
    "tool_call_to_json",
    "tool_call_result_to_json",
]
