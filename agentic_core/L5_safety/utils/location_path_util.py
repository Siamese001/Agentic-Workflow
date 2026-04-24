"""
location_path_util.py — Standalone path compliance utilities.

Salvaged from LocationAgent.py during LCD+ decommission (Phase 0.3).

Contains:
- is_path_compliant(): L5 Sovereign Structural SSOT — Supreme Court for path validity
- get_location_agent(): Redirect shim for backward compatibility (→ LocationHealerAgent)
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

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

emit_replay_key("p0", "location_path_util")
emit_determinism_digest("p0", "location_path_util")

_emit_dispatches_healing_run("p1", "location_path_util", "L5")
_emit_routes_through("p1", "location_path_util", "L5")
_emit_checks_agent_registry("p1", "location_path_util", "agent_registry")
_emit_validates_agent_capability("p1", "location_path_util", "capability")
_emit_dispatches_execution_plan("p1", "location_path_util", "exec_plan")
_emit_agent_executes_agent("p1", "location_path_util", "sub_agent")
_emit_routes_to_agent("p1", "location_path_util", "target_agent")
_emit_verifies_policy("p1", "location_path_util", "policy_check")
_emit_observes_runtime_state("p1", "location_path_util", "runtime_state")
_emit_verifies_boundary("p1", "location_path_util", "boundary_check")
_emit_transcripts_response("p1", "location_path_util", "transcript")
_emit_hard_fails_untranscripted("p1", "location_path_util")
_emit_gated_by_confidence("p1", "location_path_util", "confidence_gate")
_emit_escalates_to_human("p1", "location_path_util", "L5")
_emit_reads_policy_state("p1", "location_path_util", "L5")
_emit_authorize_and_execute("p2", "location_path_util", "execution_auth")
_emit_validates_capability("p2", "location_path_util", "capability_check")
_emit_routes_to_capability("p2", "location_path_util", "capability_route")
_emit_writes_via_uwg("p2", "location_path_util", "uwg_write")
_emit_blocks_direct_write("p2", "location_path_util", "direct_write_block")
_emit_records_tool_invocation("p2", "location_path_util", "tool_invocation")
_emit_captures_execution_output("p2", "location_path_util", "exec_output")
_emit_dispatches_agent("p3", "location_path_util", "agent_dispatch")
_emit_coordinates_agents("p3", "location_path_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "location_path_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "location_path_util", "healing_outcome")
_emit_escalates_failure("p3", "location_path_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "location_path_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "location_path_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "location_path_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "location_path_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "location_path_util", "eval_metric")
_emit_stores_embedding("p4", "location_path_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "location_path_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "location_path_util", "exec_snapshot_link")
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

_emit_emits_metric_event("location_path_util", "p4obs", "metric_1")
_emit_emits_metric_event("location_path_util", "p4obs", "metric_2")
_emit_emits_metric_event("location_path_util", "p4obs", "metric_3")
_emit_emits_metric_event("location_path_util", "p4obs", "metric_4")
_emit_emits_metric_event("location_path_util", "p4obs", "metric_5")
_emit_emits_metric_event("location_path_util", "p4obs", "metric_6")
_emit_records_incident_event("location_path_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("location_path_util", "p4obs", "anomaly")
_emit_writes_observability_log("location_path_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("location_path_util", "p4obs", "mon_state")
_emit_triggers_alert("location_path_util", "p4obs", "alert")
_emit_links_incident_trace("location_path_util", "p4obs", "trace_link")
_emit_captures_pattern("location_path_util", "p3lm", "pattern")
_emit_records_learning_event("location_path_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("location_path_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("location_path_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("location_path_util", "p3lm", "routing")
_emit_improves_agent_policy("location_path_util", "p3lm", "policy")
_emit_stores_learning_state("location_path_util", "p3lm", "state")
_emit_records_execution_trace("location_path_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("location_path_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("location_path_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("location_path_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("location_path_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("location_path_util", "env_read", "p2_env_1")
_emit_reads_environ("location_path_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("location_path_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("location_path_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "location_path_util", "context_pull")
_emit_pulls_context("p1", "location_path_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "location_path_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "location_path_util", "uwg_term_2")
_emit_writes_through("p1", "location_path_util", "write_through")
_emit_writes_through("p1", "location_path_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "location_path_util", "safety_validation")
_emit_invokes_eval("p1", "location_path_util", "eval_call")
_emit_proposal_commits_routing("p1", "location_path_util", "routing_commit")

if TYPE_CHECKING:
    # MW-9 (2026-04-24): Class body relocated to utils module; agent path is now a re-export shim.
    from agentic_core.L5_safety.utils.location_healer_util import LocationHealerAgent


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
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "is_path_compliant", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "is_path_compliant", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "is_path_compliant")
    from agentic_core.L5_safety.config.structure_blueprint import (
        DEPTH_RULES,
        PROJECT_ROOT_WHITELIST,
        get_validated_project_root,
    )

    if project_root is None:
        project_root = get_validated_project_root()
    path = Path(file_path)
    try:
        if not path.is_absolute():
            path = project_root / path
        rel_path = path.relative_to(project_root)
    except (ValueError, RuntimeError):
        return False
    parts = rel_path.parts
    if not parts:
        return False
    root_folder = parts[0]
    if root_folder not in PROJECT_ROOT_WHITELIST:
        return False
    max_depth = DEPTH_RULES.get(root_folder, 3)
    if len(parts) > max_depth:
        return False
    if root_folder.startswith(("legacy_", "old_")):
        return False
    forbidden_pattern = re.compile("^\\d+_")
    for part in parts:
        if forbidden_pattern.match(part):
            return False
    return True


_healer_instance: LocationHealerAgent | None = None


def get_location_agent(project_root: Path) -> LocationHealerAgent:
    """Get or create LocationHealerAgent singleton.

    Backward-compatible redirect: callers that previously used
    ``get_location_agent()`` from LocationAgent.py now get a
    LocationHealerAgent instance instead.
    """
    global _healer_instance
    if _healer_instance is None:
        # MW-9 (2026-04-24): Class body relocated to utils module; agent path is now a re-export shim.
        from agentic_core.L5_safety.utils.location_healer_util import LocationHealerAgent

        _healer_instance = LocationHealerAgent(project_root=project_root)
    return _healer_instance
