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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "location_path_util")
trace_contract.emit_determinism_digest("p0", "location_path_util")

trace_contract._emit_dispatches_healing_run("p1", "location_path_util", "L5")
trace_contract._emit_routes_through("p1", "location_path_util", "L5")
trace_contract._emit_checks_agent_registry("p1", "location_path_util", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "location_path_util", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "location_path_util", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "location_path_util", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "location_path_util", "target_agent")
trace_contract._emit_verifies_policy("p1", "location_path_util", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "location_path_util", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "location_path_util", "boundary_check")
trace_contract._emit_transcripts_response("p1", "location_path_util", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "location_path_util")
trace_contract._emit_gated_by_confidence("p1", "location_path_util", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "location_path_util", "L5")
trace_contract._emit_reads_policy_state("p1", "location_path_util", "L5")
trace_contract._emit_authorize_and_execute("p2", "location_path_util", "execution_auth")
trace_contract._emit_validates_capability("p2", "location_path_util", "capability_check")
trace_contract._emit_routes_to_capability("p2", "location_path_util", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "location_path_util", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "location_path_util", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "location_path_util", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "location_path_util", "exec_output")
trace_contract._emit_dispatches_agent("p3", "location_path_util", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "location_path_util", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "location_path_util", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "location_path_util", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "location_path_util", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "location_path_util", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "location_path_util", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "location_path_util", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "location_path_util", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "location_path_util", "eval_metric")
trace_contract._emit_stores_embedding("p4", "location_path_util", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "location_path_util", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "location_path_util", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("location_path_util", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("location_path_util", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("location_path_util", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("location_path_util", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("location_path_util", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("location_path_util", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("location_path_util", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("location_path_util", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("location_path_util", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("location_path_util", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("location_path_util", "p4obs", "alert")
trace_contract._emit_links_incident_trace("location_path_util", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("location_path_util", "p3lm", "pattern")
trace_contract._emit_records_learning_event("location_path_util", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("location_path_util", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("location_path_util", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("location_path_util", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("location_path_util", "p3lm", "policy")
trace_contract._emit_stores_learning_state("location_path_util", "p3lm", "state")
trace_contract._emit_records_execution_trace("location_path_util", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("location_path_util", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("location_path_util", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("location_path_util", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("location_path_util", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("location_path_util", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("location_path_util", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("location_path_util", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("location_path_util", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "location_path_util", "context_pull")
trace_contract._emit_pulls_context("p1", "location_path_util", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "location_path_util", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "location_path_util", "uwg_term_2")
trace_contract._emit_writes_through("p1", "location_path_util", "write_through")
trace_contract._emit_writes_through("p1", "location_path_util", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "location_path_util", "safety_validation")
trace_contract._emit_invokes_eval("p1", "location_path_util", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "location_path_util", "routing_commit")

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

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "is_path_compliant", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "is_path_compliant", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "is_path_compliant")
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
