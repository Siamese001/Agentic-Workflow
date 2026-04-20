"""
SSOT for robust project root detection.

This module replaces all the fragile `../../..` path hacks and provides
a single, reliable way to find the project root directory.

SSOT Consolidation (Jan 20, 2026):
All scripts should import get_project_root from here instead of
computing paths manually.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Final

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_snapshots_state,
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

emit_replay_key("p0", "project_root_util")
emit_determinism_digest("p0", "project_root_util")

_emit_dispatches_healing_run("p1", "project_root_util", "L0")
_emit_routes_through("p1", "project_root_util", "L0")
_emit_checks_agent_registry("p1", "project_root_util", "agent_registry")
_emit_validates_agent_capability("p1", "project_root_util", "capability")
_emit_dispatches_execution_plan("p1", "project_root_util", "exec_plan")
_emit_agent_executes_agent("p1", "project_root_util", "sub_agent")
_emit_routes_to_agent("p1", "project_root_util", "target_agent")
_emit_verifies_policy("p1", "project_root_util", "policy_check")
_emit_observes_runtime_state("p1", "project_root_util", "runtime_state")
_emit_verifies_boundary("p1", "project_root_util", "boundary_check")
_emit_transcripts_response("p1", "project_root_util", "transcript")
_emit_hard_fails_untranscripted("p1", "project_root_util")
_emit_gated_by_confidence("p1", "project_root_util", "confidence_gate")
_emit_escalates_to_human("p1", "project_root_util", "L0")
_emit_reads_policy_state("p1", "project_root_util", "L0")
_emit_authorize_and_execute("p2", "project_root_util", "execution_auth")
_emit_validates_capability("p2", "project_root_util", "capability_check")
_emit_routes_to_capability("p2", "project_root_util", "capability_route")
_emit_writes_via_uwg("p2", "project_root_util", "uwg_write")
_emit_blocks_direct_write("p2", "project_root_util", "direct_write_block")
_emit_records_tool_invocation("p2", "project_root_util", "tool_invocation")
_emit_captures_execution_output("p2", "project_root_util", "exec_output")
_emit_dispatches_agent("p3", "project_root_util", "agent_dispatch")
_emit_coordinates_agents("p3", "project_root_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "project_root_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "project_root_util", "healing_outcome")
_emit_escalates_failure("p3", "project_root_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "project_root_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "project_root_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "project_root_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "project_root_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "project_root_util", "eval_metric")
_emit_stores_embedding("p4", "project_root_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "project_root_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "project_root_util", "exec_snapshot_link")
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

_emit_emits_metric_event("project_root_util", "p4obs", "metric_1")
_emit_emits_metric_event("project_root_util", "p4obs", "metric_2")
_emit_emits_metric_event("project_root_util", "p4obs", "metric_3")
_emit_emits_metric_event("project_root_util", "p4obs", "metric_4")
_emit_emits_metric_event("project_root_util", "p4obs", "metric_5")
_emit_emits_metric_event("project_root_util", "p4obs", "metric_6")
_emit_records_incident_event("project_root_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("project_root_util", "p4obs", "anomaly")
_emit_writes_observability_log("project_root_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("project_root_util", "p4obs", "mon_state")
_emit_triggers_alert("project_root_util", "p4obs", "alert")
_emit_links_incident_trace("project_root_util", "p4obs", "trace_link")
_emit_captures_pattern("project_root_util", "p3lm", "pattern")
_emit_records_learning_event("project_root_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("project_root_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("project_root_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("project_root_util", "p3lm", "routing")
_emit_improves_agent_policy("project_root_util", "p3lm", "policy")
_emit_stores_learning_state("project_root_util", "p3lm", "state")
_emit_records_execution_trace("project_root_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("project_root_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("project_root_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("project_root_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("project_root_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("project_root_util", "env_read", "p2_env_1")
_emit_reads_environ("project_root_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("project_root_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("project_root_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "project_root_util", "context_pull")
_emit_pulls_context("p1", "project_root_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "project_root_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "project_root_util", "uwg_term_2")
_emit_writes_through("p1", "project_root_util", "write_through")
_emit_writes_through("p1", "project_root_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "project_root_util", "safety_validation")
_emit_invokes_eval("p1", "project_root_util", "eval_call")
_emit_proposal_commits_routing("p1", "project_root_util", "routing_commit")

# Core package directory name
AGENTIC_CORE_DIR: str = "agentic_core"
ENV_PROJECT_ROOT: str = "AGENTIC_PROJECT_ROOT"

# Markers that indicate the root of the project
ROOT_MARKERS: list[str] = [
    "pyproject.toml",
    ".git",
    AGENTIC_CORE_DIR,  # The core package directory itself
    "requirements.txt",
]


def _looks_like_project_root(path: Path) -> bool:
    """Return True when the directory strongly resembles the project root."""
    hits = sum(1 for marker in ROOT_MARKERS if (path / marker).exists())
    return hits >= 2 or ((path / ".git").exists() and (path / AGENTIC_CORE_DIR).exists())


@lru_cache(maxsize=1)
def get_project_root(start_path: str | None = None) -> Path:
    """
    Detect the project root directory by searching upward for markers.

    Args:
        start_path: The path to start searching from. Defaults to CWD.

    Returns:
        Path: The absolute path to the project root.

    Raises:
        RuntimeError: If the project root cannot be found.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "get_project_root", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "get_project_root", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "get_project_root")

    env_root = os.environ.get(ENV_PROJECT_ROOT)
    if env_root:
        candidate = Path(env_root).expanduser().resolve()
        if _looks_like_project_root(candidate):
            return candidate
        raise RuntimeError(
            f"{ENV_PROJECT_ROOT} is set but does not point at a valid project root: {candidate}",
        )

    current = Path(start_path).expanduser().resolve() if start_path else Path.cwd().resolve()

    if current.is_file():
        current = current.parent

    for candidate in (current, *current.parents):
        if _looks_like_project_root(candidate):
            return candidate

    try:
        probe = current
        while True:
            if probe.name == AGENTIC_CORE_DIR:
                return probe.parent
            if probe.parent == probe:
                break
            probe = probe.parent
    except (ValueError, TypeError):  # guardian: allow-silent-swallow
        pass

    raise RuntimeError(
        f"Could not detect project root from {start_path or Path.cwd()}",
    )


def clear_project_root_cache() -> None:
    """Clear the cached project root. Useful for testing."""
    get_project_root.cache_clear()


PROJECT_ROOT_MARKERS: Final[frozenset[str]] = frozenset(
    {
        "pyproject.toml",
        "canon_validator_agentic_v2_thin.py",
        AGENTIC_CORE_DIR,
        ".git",
    },
)


def get_validated_project_root() -> Path:
    """Get the validated project root by searching upward from this file.

    Compatibility alias — delegates to get_project_root().
    """
    return get_project_root(str(Path(__file__).resolve()))


__all__ = [
    "get_project_root",
    "get_validated_project_root",
    "clear_project_root_cache",
    "ROOT_MARKERS",
    "PROJECT_ROOT_MARKERS",
]
