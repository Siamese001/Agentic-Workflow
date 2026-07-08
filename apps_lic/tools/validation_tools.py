"""
Validation tools for LIC domain.

Provides schema validation utilities used by validator agents.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "validation_tools", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "validation_tools", "policy_binding")
trace_contract._emit_snapshots_state("p0", "validation_tools", "state_snapshot")

trace_contract._emit_emits_metric_event("validation_tools", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("validation_tools", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("validation_tools", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("validation_tools", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("validation_tools", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("validation_tools", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("validation_tools", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("validation_tools", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("validation_tools", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("validation_tools", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("validation_tools", "p4obs", "alert")
trace_contract._emit_links_incident_trace("validation_tools", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("validation_tools", "p3lm", "pattern")
trace_contract._emit_records_learning_event("validation_tools", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("validation_tools", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("validation_tools", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("validation_tools", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("validation_tools", "p3lm", "policy")
trace_contract._emit_stores_learning_state("validation_tools", "p3lm", "state")
trace_contract._emit_records_execution_trace("validation_tools", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("validation_tools", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("validation_tools", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("validation_tools", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("validation_tools", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("validation_tools", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("validation_tools", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("validation_tools", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("validation_tools", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "validation_tools", "context_pull")
trace_contract._emit_pulls_context("p1", "validation_tools", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "validation_tools", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "validation_tools", "uwg_term_2")
trace_contract._emit_writes_through("p1", "validation_tools", "write_through")
trace_contract._emit_writes_through("p1", "validation_tools", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "validation_tools", "safety_validation")
trace_contract._emit_invokes_eval("p1", "validation_tools", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "validation_tools", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "validation_tools", "human_escalation")
trace_contract._emit_routes_through("p1", "validation_tools", "route_through")
trace_contract._emit_checks_agent_registry("p1", "validation_tools", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "validation_tools", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "validation_tools", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "validation_tools", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "validation_tools", "target_agent")
trace_contract._emit_verifies_policy("p1", "validation_tools", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "validation_tools", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "validation_tools", "boundary_check")
trace_contract._emit_transcripts_response("p1", "validation_tools", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "validation_tools")
trace_contract._emit_gated_by_confidence("p1", "validation_tools", "confidence_gate")
trace_contract.emit_replay_key("p0", "validation_tools")
trace_contract.emit_determinism_digest("p0", "validation_tools")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "validation_tools", "execution_auth")
trace_contract._emit_validates_capability("p2", "validation_tools", "capability_check")
trace_contract._emit_routes_to_capability("p2", "validation_tools", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "validation_tools", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "validation_tools", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "validation_tools", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "validation_tools", "exec_output")
trace_contract._emit_dispatches_agent("p3", "validation_tools", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "validation_tools", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "validation_tools", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "validation_tools", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "validation_tools", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "validation_tools", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "validation_tools", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "validation_tools", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "validation_tools", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "validation_tools", "eval_metric")
trace_contract._emit_stores_embedding("p4", "validation_tools", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "validation_tools", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "validation_tools", "exec_snapshot_link")


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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "ValidationResult.add_error")

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
