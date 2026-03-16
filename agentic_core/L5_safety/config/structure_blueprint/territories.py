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
    SOVEREIGN_TERRITORIES,  # Internal use only - not re-exported
    SubfolderDefinition,  # noqa: F401
    TerritoryDefinition,  # noqa: F401
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "territories")
emit_determinism_digest("p0", "territories")

_emit_dispatches_healing_run("p1", "territories", "L5")
_emit_routes_through("p1", "territories", "L5")
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
    return SOVEREIGN_TERRITORIES.get(territory_name)


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
    return SOVEREIGN_TERRITORIES


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
