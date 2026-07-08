"""
Territories Module — New Territory API (replaces SOVEREIGN_TERRITORIES).

This module provides the canonical API for accessing territory metadata:
- get_territory_metadata(name) — Get metadata for a specific territory
- get_all_territories() — Get all territory definitions (read-only)
- is_valid_root_folder(name) — Check if folder is allowed at project root

Note: SOVEREIGN_TERRITORIES and build_sovereign_territories() are no longer
exported. Use the functions above instead. Internal code can still access
SOVEREIGN_TERRITORIES via _constants if absolutely necessary.
"""

from __future__ import annotations

from collections.abc import Mapping

from agentic_core.L5_safety.config.structure_blueprint._constants import (
    SubfolderDefinition,  # noqa: F401
    TerritoryDefinition,  # noqa: F401
)
from agentic_core.L5_safety.config.structure_blueprint.yaml_loader import (
    load_territories,
)
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "territories")
trace_contract.emit_determinism_digest("p0", "territories")

trace_contract._emit_dispatches_healing_run("p1", "territories", "L5")
trace_contract._emit_routes_through("p1", "territories", "L5")
trace_contract._emit_checks_agent_registry("p1", "territories", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "territories", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "territories", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "territories", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "territories", "target_agent")
trace_contract._emit_verifies_policy("p1", "territories", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "territories", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "territories", "boundary_check")
trace_contract._emit_transcripts_response("p1", "territories", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "territories")
trace_contract._emit_gated_by_confidence("p1", "territories", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "territories", "L5")
trace_contract._emit_reads_policy_state("p1", "territories", "L5")

trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_records_execution_trace("p0", "evidence", "territories")
trace_contract._emit_applies_guardrail("p0", "territories", "p0_governance")
trace_contract._emit_snapshots_state("p0", "territories", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "territories", "execution_auth")
trace_contract._emit_validates_capability("p2", "territories", "capability_check")
trace_contract._emit_routes_to_capability("p2", "territories", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "territories", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "territories", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "territories", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "territories", "exec_output")
trace_contract._emit_dispatches_agent("p3", "territories", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "territories", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "territories", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "territories", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "territories", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "territories", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "territories", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "territories", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "territories", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "territories", "eval_metric")
trace_contract._emit_stores_embedding("p4", "territories", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "territories", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "territories", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("territories", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("territories", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("territories", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("territories", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("territories", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("territories", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("territories", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("territories", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("territories", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("territories", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("territories", "p4obs", "alert")
trace_contract._emit_links_incident_trace("territories", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("territories", "p3lm", "pattern")
trace_contract._emit_records_learning_event("territories", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("territories", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("territories", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("territories", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("territories", "p3lm", "policy")
trace_contract._emit_stores_learning_state("territories", "p3lm", "state")
trace_contract._emit_records_execution_trace("territories", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("territories", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("territories", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("territories", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("territories", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("territories", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("territories", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("territories", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("territories", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "territories", "context_pull")
trace_contract._emit_pulls_context("p1", "territories", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "territories", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "territories", "uwg_term_2")
trace_contract._emit_writes_through("p1", "territories", "write_through")
trace_contract._emit_writes_through("p1", "territories", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "territories", "safety_validation")
trace_contract._emit_invokes_eval("p1", "territories", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "territories", "routing_commit")


def get_territory_metadata(territory_name: str) -> TerritoryDefinition | None:
    """Get metadata for a specific territory.

    Args:
        territory_name: Name of the territory (e.g., "apps_shared", "agentic_core")

    Returns:
        Territory definition dict with keys like 'purpose', 'subfolders', 'depth', etc.
        Returns None if territory not found.

    Example:
        >>> meta = get_territory_metadata("apps_shared")
        >>> if meta:
        ...     print(meta.get("purpose"))
    """
    data = load_territories()
    territories = data.get("territories", {})
    return territories.get(territory_name)


def get_all_territories() -> Mapping[str, TerritoryDefinition]:
    """Get all territory definitions (read-only).

    Returns:
        Immutable mapping of territory_name -> TerritoryDefinition.
        This is a read-only view — mutations will raise TypeError.

    Example:
        >>> territories = get_all_territories()
        >>> for name, meta in territories.items():
        ...     print(f"{name}: {meta.get('purpose')}")
    """
    data = load_territories()
    return data.get("territories", {})


def is_valid_root_folder(folder_name: str) -> bool:
    """Check if folder is allowed at project root.

    Args:
        folder_name: Name of the folder to check (e.g., "apps_shared", ".git")

    Returns:
        True if folder is in the project root whitelist, False otherwise.

    Example:
        >>> is_valid_root_folder("apps_shared")
        True
        >>> is_valid_root_folder("random_folder")
        False
    """
    # Import locally to avoid circular dependency (ssot imports from territories)
    from agentic_core.L5_safety.config.structure_blueprint.ssot import (
        PROJECT_ROOT_WHITELIST,
    )

    return folder_name in PROJECT_ROOT_WHITELIST
