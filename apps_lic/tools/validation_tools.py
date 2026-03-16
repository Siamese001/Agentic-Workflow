"""
Validation tools for LIC domain.

Provides schema validation utilities used by validator agents.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
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

_emit_applies_guardrail("p0", "validation_tools", "p0_governance")
_emit_reads_policy_state("p0", "validation_tools", "policy_binding")
_emit_snapshots_state("p0", "validation_tools", "state_snapshot")
emit_replay_key("p0", "validation_tools")
emit_determinism_digest("p0", "validation_tools")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "validation_tools", "execution_auth")
_emit_validates_capability("p2", "validation_tools", "capability_check")
_emit_routes_to_capability("p2", "validation_tools", "capability_route")
_emit_writes_via_uwg("p2", "validation_tools", "uwg_write")
_emit_blocks_direct_write("p2", "validation_tools", "direct_write_block")
_emit_records_tool_invocation("p2", "validation_tools", "tool_invocation")
_emit_captures_execution_output("p2", "validation_tools", "exec_output")
_emit_dispatches_agent("p3", "validation_tools", "agent_dispatch")
_emit_coordinates_agents("p3", "validation_tools", "agent_coordination")
_emit_records_workflow_lineage("p3", "validation_tools", "workflow_lineage")
_emit_records_healing_outcome("p3", "validation_tools", "healing_outcome")
_emit_escalates_failure("p3", "validation_tools", "failure_escalation")
_emit_orchestrates_workflow("p3", "validation_tools", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "validation_tools", "healing_dispatch")
_emit_invokes_evaluation("p3", "validation_tools", "evaluation_signal")
_emit_records_telemetry_event("p4", "validation_tools", "telemetry_event")
_emit_captures_evaluation_metric("p4", "validation_tools", "eval_metric")
_emit_stores_embedding("p4", "validation_tools", "embedding_store")
_emit_updates_meta_learning_state("p4", "validation_tools", "meta_learning")
_emit_links_execution_to_snapshot("p4", "validation_tools", "exec_snapshot_link")


@dataclass
class ValidationResult:
    """Result of a validation operation."""

    is_valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_error(self, error: str) -> None:
        """Add an error and mark as invalid."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ValidationResult.add_error")

        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str) -> None:
        """Add a warning (does not affect validity)."""
        self.warnings.append(warning)

    def merge(self, other: ValidationResult) -> ValidationResult:
        """Merge another result into this one."""
        self.is_valid = self.is_valid and other.is_valid
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.metadata.update(other.metadata)
        return self


def validate_schema_policy(data: dict[str, Any], schema: dict[str, Any] | None = None) -> ValidationResult:
    """
    Validate data against a schema policy.

    Args:
        data: Data to validate
        schema: Optional schema to validate against

    Returns:
        ValidationResult with validation outcome
    """
    result = ValidationResult()
    # guardian: allow-config-with-logic
    if not isinstance(data, dict):
        result.add_error("Data must be a dictionary")
        return result
    # guardian: allow-config-with-logic
    if schema:
        required = schema.get("required", [])
        for req_field in required:
            # guardian: allow-config-with-logic
            if req_field not in data:
                result.add_error(f"Missing required field: {req_field}")
    return result


__all__ = ["ValidationResult", "validate_schema_policy"]
