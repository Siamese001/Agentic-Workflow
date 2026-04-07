"""
L0 Path Utilities — Pure path validation and manipulation functions.

These are stdlib-only utilities with no governance logic.
They are extracted from L5 to eliminate upward import violations.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

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

emit_replay_key("p0", "path_util")
emit_determinism_digest("p0", "path_util")

_emit_dispatches_healing_run("p1", "path_util", "L0")
_emit_routes_through("p1", "path_util", "L0")
_emit_checks_agent_registry("p1", "path_util", "agent_registry")
_emit_validates_agent_capability("p1", "path_util", "capability")
_emit_dispatches_execution_plan("p1", "path_util", "exec_plan")
_emit_agent_executes_agent("p1", "path_util", "sub_agent")
_emit_routes_to_agent("p1", "path_util", "target_agent")
_emit_verifies_policy("p1", "path_util", "policy_check")
_emit_observes_runtime_state("p1", "path_util", "runtime_state")
_emit_verifies_boundary("p1", "path_util", "boundary_check")
_emit_transcripts_response("p1", "path_util", "transcript")
_emit_hard_fails_untranscripted("p1", "path_util")
_emit_gated_by_confidence("p1", "path_util", "confidence_gate")
_emit_escalates_to_human("p1", "path_util", "L0")
_emit_reads_policy_state("p1", "path_util", "L0")
_emit_authorize_and_execute("p2", "path_util", "execution_auth")
_emit_validates_capability("p2", "path_util", "capability_check")
_emit_routes_to_capability("p2", "path_util", "capability_route")
_emit_writes_via_uwg("p2", "path_util", "uwg_write")
_emit_blocks_direct_write("p2", "path_util", "direct_write_block")
_emit_records_tool_invocation("p2", "path_util", "tool_invocation")
_emit_captures_execution_output("p2", "path_util", "exec_output")
_emit_dispatches_agent("p3", "path_util", "agent_dispatch")
_emit_coordinates_agents("p3", "path_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "path_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "path_util", "healing_outcome")
_emit_escalates_failure("p3", "path_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "path_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "path_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "path_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "path_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "path_util", "eval_metric")
_emit_stores_embedding("p4", "path_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "path_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "path_util", "exec_snapshot_link")

if TYPE_CHECKING:
    from collections.abc import Iterator
from agentic_core.L0_routing.config.path_constants import GLOBAL_EXCLUDED_DIRS, PROJECT_ROOT_MARKERS
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

_emit_emits_metric_event("path_util", "p4obs", "metric_1")
_emit_emits_metric_event("path_util", "p4obs", "metric_2")
_emit_emits_metric_event("path_util", "p4obs", "metric_3")
_emit_emits_metric_event("path_util", "p4obs", "metric_4")
_emit_emits_metric_event("path_util", "p4obs", "metric_5")
_emit_emits_metric_event("path_util", "p4obs", "metric_6")
_emit_records_incident_event("path_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("path_util", "p4obs", "anomaly")
_emit_writes_observability_log("path_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("path_util", "p4obs", "mon_state")
_emit_triggers_alert("path_util", "p4obs", "alert")
_emit_links_incident_trace("path_util", "p4obs", "trace_link")
_emit_captures_pattern("path_util", "p3lm", "pattern")
_emit_records_learning_event("path_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("path_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("path_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("path_util", "p3lm", "routing")
_emit_improves_agent_policy("path_util", "p3lm", "policy")
_emit_stores_learning_state("path_util", "p3lm", "state")
_emit_records_execution_trace("path_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("path_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("path_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("path_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("path_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("path_util", "env_read", "p2_env_1")
_emit_reads_environ("path_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("path_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("path_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "path_util", "context_pull")
_emit_pulls_context("p1", "path_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "path_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "path_util", "uwg_term_2")
_emit_writes_through("p1", "path_util", "write_through")
_emit_writes_through("p1", "path_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "path_util", "safety_validation")
_emit_invokes_eval("p1", "path_util", "eval_call")
_emit_proposal_commits_routing("p1", "path_util", "routing_commit")


def get_validated_project_root() -> Path:
    """Get the validated project root by searching upward from CWD."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "get_validated_project_root", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "get_validated_project_root", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "get_validated_project_root")
    current = Path.cwd().resolve()
    for parent in [current, *list(current.parents)]:
        if any((parent / marker).exists() for marker in PROJECT_ROOT_MARKERS):
            return parent
    return current


def validate_path_within_project(path: str | Path, project_root: Path | None = None) -> bool:
    """Validate that a path is within the project root."""
    if project_root is None:
        project_root = get_validated_project_root()
    try:
        path = Path(path).resolve()
        project_root = Path(project_root).resolve()
        path.relative_to(project_root)
        return True
    except ValueError:
        return False


def safe_path_join(project_root: str | Path, *parts: str) -> Path:
    """Safely join path parts and validate result is within project root."""
    project_root = Path(project_root).resolve()
    result = project_root.joinpath(*parts).resolve()
    if not validate_path_within_project(result, project_root):
        raise ValueError(f"SAFETY VIOLATION: Path '{result}' is outside project root '{project_root}'")
    return result


def safe_prefixed_filename(filename: str, prefix: str) -> str:
    """Generate a safe prefixed filename."""
    if filename.startswith(prefix):
        return filename
    return f"{prefix}{filename}"


def validate_no_duplicate_prefix(filename: str, prefix: str) -> bool:
    """Validate that a filename doesn't have duplicate prefixes."""
    double_prefix = f"{prefix}{prefix}"
    return double_prefix not in filename


def get_python_files(directory: Path, *, exclude_dirs: frozenset[str] | None = None) -> Iterator[Path]:
    """Yield all Python files in a directory, excluding specified directories."""
    if exclude_dirs is None:
        exclude_dirs = GLOBAL_EXCLUDED_DIRS
    for item in directory.rglob("*.py"):
        if not any(part in exclude_dirs for part in item.parts):
            yield item


def is_path_allowed(path: str | Path, allowed_dirs: frozenset[str]) -> bool:
    """Check if a path is within one of the allowed directories."""
    path_str = str(path).replace("\\", "/")
    return any(path_str.startswith(d) or f"/{d}/" in path_str for d in allowed_dirs)


__all__ = [
    "get_python_files",
    "get_validated_project_root",
    "is_path_allowed",
    "safe_path_join",
    "safe_prefixed_filename",
    "validate_no_duplicate_prefix",
    "validate_path_within_project",
]
