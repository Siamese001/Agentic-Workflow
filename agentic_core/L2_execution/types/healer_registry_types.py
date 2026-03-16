"""
Healer Registry — Declarative mapping of check_id to healer function.

Each healer receives the full check dict from the guardian aggregate
and returns a HealCheckResult. Healers may accept optional keyword
arguments (repo_root, apply) for mutating mode support.
"""

from __future__ import annotations

from typing import Callable

from agentic_core.L2_execution.healers.architecture_governance_healer import (
    heal_import_compliance,
    heal_layer_gravity,
)
from agentic_core.L2_execution.healers.architecture_governor_healer import (
    heal_architecture_governance,
)
from agentic_core.L2_execution.healers.classification_compliance_healer import (
    heal_naming_compliance,
    heal_territory_compliance,
)
from agentic_core.L2_execution.healers.drift_detection_healer import (
    heal_guardian_drift_detection,
)
from agentic_core.L2_execution.healers.file_classification_healer import (
    heal_file_classification,
)
from agentic_core.L2_execution.healers.filesystem_ssot_healer import (
    heal_filesystem_ssot_drift,
)
from agentic_core.L2_execution.healers.gravity_leak_healer import (
    heal_gravity_violations,
)
from agentic_core.L2_execution.healers.hierarchy_agent_healer import (
    heal_hierarchy_violations,
)
from agentic_core.L2_execution.healers.hierarchy_compliance_healer import (
    heal_missing_structure,
    heal_subfolder_compliance,
)
from agentic_core.L2_execution.types.heal_contract_types import HealCheckResult
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

emit_replay_key("p0", "healer_registry_types")
emit_determinism_digest("p0", "healer_registry_types")

_emit_dispatches_healing_run("p1", "healer_registry_types", "L2")
_emit_routes_through("p1", "healer_registry_types", "L2")
_emit_escalates_to_human("p1", "healer_registry_types", "L2")
_emit_reads_policy_state("p1", "healer_registry_types", "L2")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "healer_registry_types")
_emit_applies_guardrail("p0", "healer_registry_types", "p0_governance")
_emit_snapshots_state("p0", "healer_registry_types", "state_snapshot")
_emit_authorize_and_execute("p2", "healer_registry_types", "execution_auth")
_emit_validates_capability("p2", "healer_registry_types", "capability_check")
_emit_routes_to_capability("p2", "healer_registry_types", "capability_route")
_emit_writes_via_uwg("p2", "healer_registry_types", "uwg_write")
_emit_blocks_direct_write("p2", "healer_registry_types", "direct_write_block")
_emit_records_tool_invocation("p2", "healer_registry_types", "tool_invocation")
_emit_captures_execution_output("p2", "healer_registry_types", "exec_output")
_emit_dispatches_agent("p3", "healer_registry_types", "agent_dispatch")
_emit_coordinates_agents("p3", "healer_registry_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "healer_registry_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "healer_registry_types", "healing_outcome")
_emit_escalates_failure("p3", "healer_registry_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "healer_registry_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "healer_registry_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "healer_registry_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "healer_registry_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "healer_registry_types", "eval_metric")
_emit_stores_embedding("p4", "healer_registry_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "healer_registry_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "healer_registry_types", "exec_snapshot_link")

HealerFn = Callable[..., HealCheckResult]

HEALER_REGISTRY: dict[str, HealerFn] = {
    "guardian_drift_detection": heal_guardian_drift_detection,
    "naming_compliance": heal_naming_compliance,
    "territory_compliance": heal_territory_compliance,
    "missing_structure": heal_missing_structure,
    "subfolder_compliance": heal_subfolder_compliance,
    "import_compliance": heal_import_compliance,
    "layer_gravity": heal_layer_gravity,
    "filesystem_ssot_drift": heal_filesystem_ssot_drift,
    "hierarchy_violations": heal_hierarchy_violations,
    "architecture_governance": heal_architecture_governance,
    "gravity_violations": heal_gravity_violations,
    "file_classification": heal_file_classification,
}

__all__ = ["HealerFn", "HEALER_REGISTRY"]
