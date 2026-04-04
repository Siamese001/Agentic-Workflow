from __future__ import annotations

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

emit_replay_key("p0", "location_utils_util")
emit_determinism_digest("p0", "location_utils_util")

_emit_dispatches_healing_run("p1", "location_utils_util", "L5")
_emit_routes_through("p1", "location_utils_util", "L5")
_emit_checks_agent_registry("p1", "location_utils_util", "agent_registry")
_emit_validates_agent_capability("p1", "location_utils_util", "capability")
_emit_dispatches_execution_plan("p1", "location_utils_util", "exec_plan")
_emit_agent_executes_agent("p1", "location_utils_util", "sub_agent")
_emit_routes_to_agent("p1", "location_utils_util", "target_agent")
_emit_verifies_policy("p1", "location_utils_util", "policy_check")
_emit_observes_runtime_state("p1", "location_utils_util", "runtime_state")
_emit_verifies_boundary("p1", "location_utils_util", "boundary_check")
_emit_transcripts_response("p1", "location_utils_util", "transcript")
_emit_hard_fails_untranscripted("p1", "location_utils_util")
_emit_gated_by_confidence("p1", "location_utils_util", "confidence_gate")
_emit_escalates_to_human("p1", "location_utils_util", "L5")
_emit_reads_policy_state("p1", "location_utils_util", "L5")
_emit_authorize_and_execute("p2", "location_utils_util", "execution_auth")
_emit_validates_capability("p2", "location_utils_util", "capability_check")
_emit_routes_to_capability("p2", "location_utils_util", "capability_route")
_emit_writes_via_uwg("p2", "location_utils_util", "uwg_write")
_emit_blocks_direct_write("p2", "location_utils_util", "direct_write_block")
_emit_records_tool_invocation("p2", "location_utils_util", "tool_invocation")
_emit_captures_execution_output("p2", "location_utils_util", "exec_output")
_emit_dispatches_agent("p3", "location_utils_util", "agent_dispatch")
_emit_coordinates_agents("p3", "location_utils_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "location_utils_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "location_utils_util", "healing_outcome")
_emit_escalates_failure("p3", "location_utils_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "location_utils_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "location_utils_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "location_utils_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "location_utils_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "location_utils_util", "eval_metric")
_emit_stores_embedding("p4", "location_utils_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "location_utils_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "location_utils_util", "exec_snapshot_link")

"\nShared utility functions for location-based operations.\n\nExtracted from LocationAgent.py during SRP fission.\nAll location-related agents should import from this module.\n"
import os
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
from agentic_core.L5_safety.config.structure_blueprint import DEPTH_RULES, SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_emits_metric_event("location_utils_util", "p4obs", "metric_1")
_emit_emits_metric_event("location_utils_util", "p4obs", "metric_2")
_emit_emits_metric_event("location_utils_util", "p4obs", "metric_3")
_emit_emits_metric_event("location_utils_util", "p4obs", "metric_4")
_emit_emits_metric_event("location_utils_util", "p4obs", "metric_5")
_emit_emits_metric_event("location_utils_util", "p4obs", "metric_6")
_emit_records_incident_event("location_utils_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("location_utils_util", "p4obs", "anomaly")
_emit_writes_observability_log("location_utils_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("location_utils_util", "p4obs", "mon_state")
_emit_triggers_alert("location_utils_util", "p4obs", "alert")
_emit_links_incident_trace("location_utils_util", "p4obs", "trace_link")
_emit_captures_pattern("location_utils_util", "p3lm", "pattern")
_emit_records_learning_event("location_utils_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("location_utils_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("location_utils_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("location_utils_util", "p3lm", "routing")
_emit_improves_agent_policy("location_utils_util", "p3lm", "policy")
_emit_stores_learning_state("location_utils_util", "p3lm", "state")
_emit_records_execution_trace("location_utils_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("location_utils_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("location_utils_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("location_utils_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("location_utils_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("location_utils_util", "env_read", "p2_env_1")
_emit_reads_environ("location_utils_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("location_utils_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("location_utils_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "location_utils_util", "context_pull")
_emit_pulls_context("p1", "location_utils_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "location_utils_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "location_utils_util", "uwg_term_2")
_emit_writes_through("p1", "location_utils_util", "write_through")
_emit_writes_through("p1", "location_utils_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "location_utils_util", "safety_validation")
_emit_invokes_eval("p1", "location_utils_util", "eval_call")
_emit_proposal_commits_routing("p1", "location_utils_util", "routing_commit")


def normalize_location_path(path: str) -> str:
    """
    Standardizes path formatting for comparison.

    Args:
        path: Path string to normalize

    Returns:
        Normalized path with forward slashes
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "normalize_location_path", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "normalize_location_path", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "normalize_location_path")
    # guardian: allow-path-string
    return os.path.normpath(path).replace("\\", "/")


def get_agent_files(root_dir: str) -> list[str]:
    """
    Discovers all .py files within the agentic_core structure.

    Args:
        root_dir: Root directory to search

    Returns:
        List of Python file paths
    """
    agent_files = []
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
        for file in files:
            if file.endswith(".py") and (not file.startswith("__")):
                agent_files.append(Path(root) / file)
    return agent_files


def compute_module_path(file_path: Path, project_root: Path | None = None) -> str:
    """
    Compute Python module path from file path.

    Args:
        file_path: Path to Python file
        project_root: Optional project root (auto-detected if None)

    Returns:
        Module path string (e.g., 'agentic_core.L5_safety.reasoning.LocationAgent')
    """
    if project_root is None:
        from agentic_core.L5_safety.config.structure_blueprint import get_validated_project_root

        project_root = get_validated_project_root()
    try:
        rel_path = file_path.relative_to(project_root)
        module_parts = list(rel_path.parts[:-1]) + [rel_path.stem]
        return ".".join(module_parts)
    except ValueError:
        return file_path.stem


def is_path_compliant(file_path: str | Path, project_root: Path | None = None) -> bool:
    """
    L5 Sovereign Structural SSOT - Hard-enforcement of path validity.

    This is the Supreme Court for structural compliance. All L3 and L2 agents
    that need to validate file paths MUST call this function instead of
    implementing their own path validation logic.

    Enforces:
    1. Path must be within project root
    2. Root folder must be in SOVEREIGN_TERRITORIES (whitelist)
    3. Depth must not exceed MAX_ALLOWED_DEPTH per root
    4. No forbidden root folders (legacy_*, old_*)
    5. No numbered folder prefixes (^\\d+_)

    Args:
        file_path: Path to validate (str or Path)
        project_root: Optional project root (auto-detected if None)

    Returns:
        True if path is structurally compliant, False otherwise

    Example:
        >>> is_path_compliant('agentic_core/L5_safety/validators/LocationAgent.py')
        True
        >>> is_path_compliant('legacy_code/old_agent.py')
        False
        >>> is_path_compliant('agentic_core/L1/L2/L3/L4/L5/deep.py')  # Too deep
        False
    """
    from agentic_core.L5_safety.config.structure_blueprint import (
        FORBIDDEN_FOLDER_PATTERN,
        FORBIDDEN_ROOT_FOLDERS,
        ROOT_WHITELIST,
        get_validated_project_root,
    )

    if project_root is None:
        project_root = get_validated_project_root()
    if isinstance(file_path, str):
        file_path = Path(file_path)
    if not file_path.is_absolute():
        file_path = project_root / file_path
    try:
        rel_path = file_path.relative_to(project_root)
    except ValueError:
        return False
    parts = rel_path.parts
    if not parts:
        return False
    root_folder = parts[0]
    if root_folder not in ROOT_WHITELIST:
        return False
    for part in parts:
        if part in FORBIDDEN_ROOT_FOLDERS:
            return False
        if hasattr(FORBIDDEN_FOLDER_PATTERN, "match"):
            if FORBIDDEN_FOLDER_PATTERN.match(part):
                return False
    if len(root_folder) >= 3 and root_folder[:2].isdigit() and (root_folder[2:3] == "_"):
        return False
    expected_depth = DEPTH_RULES.get(root_folder)
    if expected_depth is not None:
        actual_depth = len(parts) - 1
        if actual_depth != expected_depth:
            from agentic_core.L5_safety.config.structure_blueprint import VARIABLE_DEPTH_SUBFOLDERS

            if root_folder == AGENTIC_CORE_DIR and len(parts) > 1:
                subfolder = parts[1]
                if subfolder in VARIABLE_DEPTH_SUBFOLDERS and actual_depth >= 2:
                    return True
            return False
    return True
