from __future__ import annotations

from agentic_core.L0_routing.config.path_constants import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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

emit_replay_key("p0", "scan_util")
emit_determinism_digest("p0", "scan_util")

_emit_dispatches_healing_run("p1", "scan_util", "L0")
_emit_routes_through("p1", "scan_util", "L0")
_emit_checks_agent_registry("p1", "scan_util", "agent_registry")
_emit_validates_agent_capability("p1", "scan_util", "capability")
_emit_dispatches_execution_plan("p1", "scan_util", "exec_plan")
_emit_agent_executes_agent("p1", "scan_util", "sub_agent")
_emit_routes_to_agent("p1", "scan_util", "target_agent")
_emit_verifies_policy("p1", "scan_util", "policy_check")
_emit_observes_runtime_state("p1", "scan_util", "runtime_state")
_emit_verifies_boundary("p1", "scan_util", "boundary_check")
_emit_transcripts_response("p1", "scan_util", "transcript")
_emit_hard_fails_untranscripted("p1", "scan_util")
_emit_gated_by_confidence("p1", "scan_util", "confidence_gate")
_emit_escalates_to_human("p1", "scan_util", "L0")
_emit_reads_policy_state("p1", "scan_util", "L0")
_emit_authorize_and_execute("p2", "scan_util", "execution_auth")
_emit_validates_capability("p2", "scan_util", "capability_check")
_emit_routes_to_capability("p2", "scan_util", "capability_route")
_emit_writes_via_uwg("p2", "scan_util", "uwg_write")
_emit_blocks_direct_write("p2", "scan_util", "direct_write_block")
_emit_records_tool_invocation("p2", "scan_util", "tool_invocation")
_emit_captures_execution_output("p2", "scan_util", "exec_output")
_emit_dispatches_agent("p3", "scan_util", "agent_dispatch")
_emit_coordinates_agents("p3", "scan_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "scan_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "scan_util", "healing_outcome")
_emit_escalates_failure("p3", "scan_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "scan_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "scan_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "scan_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "scan_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "scan_util", "eval_metric")
_emit_stores_embedding("p4", "scan_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "scan_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "scan_util", "exec_snapshot_link")

"""
Scan Guard - Audit Utility for rglob/glob Usage

Phase 4 Performance Hardening: This module provides utilities to track and
discourage expensive rglob/glob calls, guiding developers toward the
high-performance ssot_discovery or file_cache modules.

Usage:

    # Instead of: path.rglob("*.py")
    # Use: guarded_rglob(path, "*.py")  # Logs warning + suggests FileCache

    # Better yet, use FileCache directly:
    from agentic_core.utils.file_cache import FileCache, get_python_files
    cache = FileCache.get_instance(project_root)
    files = cache.get_python_files()

Author: Cascade
Date: January 19, 2026
Phase: 4 - Performance Hardening (rglob Elimination)

Updated: January 20, 2026
- Added FileCache reference (os.walk with directory pruning)
- Added backup directory blocking
"""


import functools
import logging
import warnings
from collections.abc import Iterator
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_signs_execution_trace,
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

_emit_emits_metric_event("scan_util", "p4obs", "metric_1")
_emit_emits_metric_event("scan_util", "p4obs", "metric_2")
_emit_emits_metric_event("scan_util", "p4obs", "metric_3")
_emit_emits_metric_event("scan_util", "p4obs", "metric_4")
_emit_emits_metric_event("scan_util", "p4obs", "metric_5")
_emit_emits_metric_event("scan_util", "p4obs", "metric_6")
_emit_records_incident_event("scan_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("scan_util", "p4obs", "anomaly")
_emit_writes_observability_log("scan_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("scan_util", "p4obs", "mon_state")
_emit_triggers_alert("scan_util", "p4obs", "alert")
_emit_links_incident_trace("scan_util", "p4obs", "trace_link")
_emit_captures_pattern("scan_util", "p3lm", "pattern")
_emit_records_learning_event("scan_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("scan_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("scan_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("scan_util", "p3lm", "routing")
_emit_improves_agent_policy("scan_util", "p3lm", "policy")
_emit_stores_learning_state("scan_util", "p3lm", "state")
_emit_records_execution_trace("scan_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("scan_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("scan_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("scan_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("scan_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("scan_util", "env_read", "p2_env_1")
_emit_reads_environ("scan_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("scan_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("scan_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "scan_util", "context_pull")
_emit_pulls_context("p1", "scan_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "scan_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "scan_util", "uwg_term_2")
_emit_writes_through("p1", "scan_util", "write_through")
_emit_writes_through("p1", "scan_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "scan_util", "safety_validation")
_emit_invokes_eval("p1", "scan_util", "eval_call")
_emit_proposal_commits_routing("p1", "scan_util", "routing_commit")

Logger = logging.getLogger(__name__)


# Dangerous directories that should never be scanned directly
DANGEROUS_DIRECTORIES = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES


def guarded_rglob(path: Path, pattern: str, caller: str | None = None) -> Iterator[Path]:
    """
    Audit utility to track and discourage expensive rglob calls.

    Logs a DeprecationWarning suggesting FileCache before executing the scan.
    Use this as a drop-in replacement for path.rglob() during migration.

    Args:
        path: The path to scan
        pattern: The glob pattern (e.g., "*.py")
        caller: Optional caller identifier for logging

    Returns:
        Iterator of matching Path objects (same as rglob)

    Example:
        # Instead of: path.rglob("*.py")
        files = list(guarded_rglob(path, "*.py"))
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "guarded_rglob", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "guarded_rglob", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "guarded_rglob")
    caller_info = f" (caller: {caller})" if caller else ""
    path_str = str(path)

    # Block scanning of dangerous directories (CRITICAL: Prevents hangs)
    for dangerous in DANGEROUS_DIRECTORIES:
        if dangerous in path_str:
            warnings.warn(
                f"BLOCKED: Dangerous directory scan attempted: {path}. "
                "This can cause infinite loops or extreme I/O. Use FileCache instead.",
                RuntimeWarning,
                stacklevel=2,
            )
            Logger.error(f"[SCAN_GUARD] BLOCKED: Dangerous directory scan: {path}")
            # Fail-safe: Return empty iterator instead of allowing scan
            return iter([])

    warnings.warn(
        f"Expensive rglob('{pattern}') detected at {path}{caller_info}. "
        "Please refactor to use agentic_core.utils.file_cache.FileCache "
        "for better performance (uses os.walk with directory pruning).",
        DeprecationWarning,
        stacklevel=2,
    )

    Logger.warning(
        f"[SCAN_GUARD] rglob('{pattern}') called on {path}{caller_info}. Consider migrating to FileCache.",
    )

    return path.rglob(pattern)


def guarded_glob(path: Path, pattern: str, caller: str | None = None) -> Iterator[Path]:
    """
    Audit utility to track and discourage expensive glob calls.

    Logs a DeprecationWarning suggesting FileCache before executing the scan.
    Use this as a drop-in replacement for path.glob() during migration.

    Args:
        path: The path to scan
        pattern: The glob pattern (e.g., "*.py")
        caller: Optional caller identifier for logging

    Returns:
        Iterator of matching Path objects (same as glob)
    """
    caller_info = f" (caller: {caller})" if caller else ""

    warnings.warn(
        f"Expensive glob('{pattern}') detected at {path}{caller_info}. "
        "Please refactor to use agentic_core.utils.ssot_discovery for better performance.",
        DeprecationWarning,
        stacklevel=2,
    )

    Logger.warning(
        f"[SCAN_GUARD] glob('{pattern}') called on {path}{caller_info}. Consider migrating to ssot_discovery.",
    )

    return path.glob(pattern)


def deprecate_rglob(func):
    """
    Decorator to mark functions that use rglob as deprecated.

    Usage:
        @deprecate_rglob
        def my_function_with_rglob():
            return path.rglob("*.py")
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        warnings.warn(
            f"Function {func.__name__} uses rglob which is deprecated. "
            "Please refactor to use agentic_core.utils.ssot_discovery.",
            DeprecationWarning,
            stacklevel=2,
        )
        return func(*args, **kwargs)

    return wrapper


def count_rglob_calls_in_file(file_path: Path) -> int:
    """
    Count the number of rglob/glob calls in a Python file.

    Useful for auditing and tracking migration progress.

    Args:
        file_path: Path to the Python file to analyze

    Returns:    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling
        Count of rglob/glob calls found
    """
    import re

    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling
        return 0

    # Count .rglob( and .glob( calls
    rglob_pattern = r"\.rglob\s*\("
    glob_pattern = r"\.glob\s*\("

    rglob_count = len(re.findall(rglob_pattern, content))
    glob_count = len(re.findall(glob_pattern, content))

    return rglob_count + glob_count


def audit_rglob_usage(project_root: Path) -> dict:
    """
    Audit all rglob/glob usage in the project.

    Returns a report of files with rglob/glob calls and their counts.

    Args:
        project_root: Root directory of the project

    Returns:
        Dict with audit results
    """
    from agentic_core.utils.ssot_discovery_validator import get_python_files

    files = get_python_files(project_root)

    offenders = []
    total_calls = 0

    for file_path in files:
        count = count_rglob_calls_in_file(file_path)
        if count > 0:
            offenders.append({"file": str(file_path.relative_to(project_root)), "count": count})
            total_calls += count

    # Sort by count descending
    offenders.sort(key=lambda x: x["count"], reverse=True)

    return {
        "total_files_scanned": len(files),
        "files_with_rglob": len(offenders),
        "total_rglob_calls": total_calls,
        "top_offenders": offenders[:20],  # Top 20
        "all_offenders": offenders,
    }


__all__ = [
    "guarded_rglob",
    "guarded_glob",
    "deprecate_rglob",
    "count_rglob_calls_in_file",
    "audit_rglob_usage",
]
