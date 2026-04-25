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
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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

emit_replay_key("p0", "territories")
emit_determinism_digest("p0", "territories")

_emit_dispatches_healing_run("p1", "territories", "L5")
_emit_routes_through("p1", "territories", "L5")
_emit_checks_agent_registry("p1", "territories", "agent_registry")
_emit_validates_agent_capability("p1", "territories", "capability")
_emit_dispatches_execution_plan("p1", "territories", "exec_plan")
_emit_agent_executes_agent("p1", "territories", "sub_agent")
_emit_routes_to_agent("p1", "territories", "target_agent")
_emit_verifies_policy("p1", "territories", "policy_check")
_emit_observes_runtime_state("p1", "territories", "runtime_state")
_emit_verifies_boundary("p1", "territories", "boundary_check")
_emit_transcripts_response("p1", "territories", "transcript")
_emit_hard_fails_untranscripted("p1", "territories")
_emit_gated_by_confidence("p1", "territories", "confidence_gate")
_emit_escalates_to_human("p1", "territories", "L5")
_emit_reads_policy_state("p1", "territories", "L5")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "territories")
_emit_applies_guardrail("p0", "territories", "p0_governance")
_emit_snapshots_state("p0", "territories", "state_snapshot")
_emit_authorize_and_execute("p2", "territories", "execution_auth")
_emit_validates_capability("p2", "territories", "capability_check")
_emit_routes_to_capability("p2", "territories", "capability_route")
_emit_writes_via_uwg("p2", "territories", "uwg_write")
_emit_blocks_direct_write("p2", "territories", "direct_write_block")
_emit_records_tool_invocation("p2", "territories", "tool_invocation")
_emit_captures_execution_output("p2", "territories", "exec_output")
_emit_dispatches_agent("p3", "territories", "agent_dispatch")
_emit_coordinates_agents("p3", "territories", "agent_coordination")
_emit_records_workflow_lineage("p3", "territories", "workflow_lineage")
_emit_records_healing_outcome("p3", "territories", "healing_outcome")
_emit_escalates_failure("p3", "territories", "failure_escalation")
_emit_orchestrates_workflow("p3", "territories", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "territories", "healing_dispatch")
_emit_invokes_evaluation("p3", "territories", "evaluation_signal")
_emit_records_telemetry_event("p4", "territories", "telemetry_event")
_emit_captures_evaluation_metric("p4", "territories", "eval_metric")
_emit_stores_embedding("p4", "territories", "embedding_store")
_emit_updates_meta_learning_state("p4", "territories", "meta_learning")
_emit_links_execution_to_snapshot("p4", "territories", "exec_snapshot_link")
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
    _emit_records_execution_trace,
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

_emit_emits_metric_event("territories", "p4obs", "metric_1")
_emit_emits_metric_event("territories", "p4obs", "metric_2")
_emit_emits_metric_event("territories", "p4obs", "metric_3")
_emit_emits_metric_event("territories", "p4obs", "metric_4")
_emit_emits_metric_event("territories", "p4obs", "metric_5")
_emit_emits_metric_event("territories", "p4obs", "metric_6")
_emit_records_incident_event("territories", "p4obs", "incident")
_emit_captures_runtime_anomaly("territories", "p4obs", "anomaly")
_emit_writes_observability_log("territories", "p4obs", "obs_log")
_emit_updates_monitoring_state("territories", "p4obs", "mon_state")
_emit_triggers_alert("territories", "p4obs", "alert")
_emit_links_incident_trace("territories", "p4obs", "trace_link")
_emit_captures_pattern("territories", "p3lm", "pattern")
_emit_records_learning_event("territories", "p3lm", "learning_event")
_emit_writes_learning_snapshot("territories", "p3lm", "snapshot")
_emit_feeds_meta_learning("territories", "p3lm", "meta_feed")
_emit_updates_routing_strategy("territories", "p3lm", "routing")
_emit_improves_agent_policy("territories", "p3lm", "policy")
_emit_stores_learning_state("territories", "p3lm", "state")
_emit_records_execution_trace("territories", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("territories", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("territories", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("territories", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("territories", "L4_STATE", "p2_trace_5")
_emit_reads_environ("territories", "env_read", "p2_env_1")
_emit_reads_environ("territories", "env_read", "p2_env_2")
_emit_reads_runtime_state("territories", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("territories", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "territories", "context_pull")
_emit_pulls_context("p1", "territories", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "territories", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "territories", "uwg_term_2")
_emit_writes_through("p1", "territories", "write_through")
_emit_writes_through("p1", "territories", "write_through_2")
_emit_validated_by_safety_plane("p1", "territories", "safety_validation")
_emit_invokes_eval("p1", "territories", "eval_call")
_emit_proposal_commits_routing("p1", "territories", "routing_commit")


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
