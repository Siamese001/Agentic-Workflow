"""
Shared constants for Location Validation and Healing.

Extracted from LocationAgent.py during SRP fission.
All location-related agents should import from this module.
"""

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

emit_replay_key("p0", "location_constants_util")
emit_determinism_digest("p0", "location_constants_util")

_emit_dispatches_healing_run("p1", "location_constants_util", "L5")
_emit_routes_through("p1", "location_constants_util", "L5")
_emit_escalates_to_human("p1", "location_constants_util", "L5")
_emit_reads_policy_state("p1", "location_constants_util", "L5")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "location_constants_util")
_emit_applies_guardrail("p0", "location_constants_util", "p0_governance")
_emit_snapshots_state("p0", "location_constants_util", "state_snapshot")
_emit_authorize_and_execute("p2", "location_constants_util", "execution_auth")
_emit_validates_capability("p2", "location_constants_util", "capability_check")
_emit_routes_to_capability("p2", "location_constants_util", "capability_route")
_emit_writes_via_uwg("p2", "location_constants_util", "uwg_write")
_emit_blocks_direct_write("p2", "location_constants_util", "direct_write_block")
_emit_records_tool_invocation("p2", "location_constants_util", "tool_invocation")
_emit_captures_execution_output("p2", "location_constants_util", "exec_output")
_emit_dispatches_agent("p3", "location_constants_util", "agent_dispatch")
_emit_coordinates_agents("p3", "location_constants_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "location_constants_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "location_constants_util", "healing_outcome")
_emit_escalates_failure("p3", "location_constants_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "location_constants_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "location_constants_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "location_constants_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "location_constants_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "location_constants_util", "eval_metric")
_emit_stores_embedding("p4", "location_constants_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "location_constants_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "location_constants_util", "exec_snapshot_link")

# Archive subfolder mapping for violation types
ARCHIVE_SUBFOLDERS: dict[str, str] = {
    "VOID VIOLATION": "void_violations",
    "GRAVITY": "void_violations",
    "LAYER PREFIX VIOLATION": "naming_violations",
}

# Default archive subfolder for unclassified violations
DEFAULT_ARCHIVE_SUBFOLDER: str = "location_violations"

# Healing strategy mapping (violation type → method name)
# CRITICAL: VOID VIOLATION must be handled BEFORE falling back to archiving
# The correct flow is: relocate → propose new subfolder → update SSOT → archive (last resort)
HEALING_STRATEGY_MAP: dict[str, str] = {
    "BROKEN BACKUP": "_heal_broken_backup",
    "APP-SPECIFIC IN CORE": "_heal_app_specific_violation",
    "TERRITORY MISMATCH": "_heal_territory_mismatch",
    "DEEP VIOLATION": "_heal_depth_violation",
    "SHALLOW VIOLATION": "_heal_depth_violation",
    "PASCAL_IN_NON_AGENT_FOLDER": "_heal_app_specific_violation",
    "VOID VIOLATION": "_heal_void_violation",  # NEW: Handle void violations properly
}

# Default app healing target subfolder
DEFAULT_APP_HEALING_TARGET: str = "reasoning"

# Violation severity thresholds
VIOLATION_THRESHOLDS: dict[str, int] = {
    "critical": 10,
    "high": 25,
    "medium": 50,
}

# Default report path
DEFAULT_REPORT_PATH: str = "reports/location_audit.json"
