from __future__ import annotations

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

emit_replay_key("p0", "validation_types")
emit_determinism_digest("p0", "validation_types")

_emit_dispatches_healing_run("p1", "validation_types", "L1")
_emit_routes_through("p1", "validation_types", "L1")
_emit_escalates_to_human("p1", "validation_types", "L1")
_emit_reads_policy_state("p1", "validation_types", "L1")

_emit_snapshots_state("p0", "validation_types", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "validation_types", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "validation_types")
_emit_authorize_and_execute("p2", "validation_types", "execution_auth")
_emit_validates_capability("p2", "validation_types", "capability_check")
_emit_routes_to_capability("p2", "validation_types", "capability_route")
_emit_writes_via_uwg("p2", "validation_types", "uwg_write")
_emit_blocks_direct_write("p2", "validation_types", "direct_write_block")
_emit_records_tool_invocation("p2", "validation_types", "tool_invocation")
_emit_captures_execution_output("p2", "validation_types", "exec_output")
_emit_dispatches_agent("p3", "validation_types", "agent_dispatch")
_emit_coordinates_agents("p3", "validation_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "validation_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "validation_types", "healing_outcome")
_emit_escalates_failure("p3", "validation_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "validation_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "validation_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "validation_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "validation_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "validation_types", "eval_metric")
_emit_stores_embedding("p4", "validation_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "validation_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "validation_types", "exec_snapshot_link")

"\nValidation Protocol - Dependency Inversion for L1 → L4\nDefines the interface L1 needs without depending on L4 implementation.\n"
from typing import Any, Protocol


class IValidationProtocol(Protocol):
    """Protocol defining the validation context interface needed by L1.

    This inverts the L1 → L4 dependency by defining the interface in L1
    that L4's ValidationContext must implement.
    """

    def get_file_path(self) -> str:
        """Get the file path being validated."""
        ...

    def get_project_root(self) -> str:
        """Get the project root path."""
        ...

    def add_violation(self, key: int, message: str, Severity: str = "error") -> None:
        """Add a validation Violation."""
        ...

    def get_violations(self) -> list[dict[str, Any]]:
        """Get all recorded violations."""
        ...

    def has_violations(self) -> bool:
        """Check if any violations were recorded."""
        ...

    def get_cache(self, key: str) -> Any | None:
        """Get cached value."""
        ...

    def set_cache(self, key: str, value: Any) -> None:
        """Set cached value."""
        ...

    def get_metadata(self, key: str) -> Any | None:
        """Get metadata value."""
        ...

    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata value."""
        ...
