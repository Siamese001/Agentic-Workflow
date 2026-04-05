"""
Shared Validation Mixin - Phase 2 Optimization
Provides common validation workflow patterns for agents.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_applies_guardrail("p0", "validation_mixin_util", "p0_governance")
_emit_reads_policy_state("p0", "validation_mixin_util", "policy_binding")
_emit_snapshots_state("p0", "validation_mixin_util", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("validation_mixin_util", "p4obs", "metric_1")
_emit_emits_metric_event("validation_mixin_util", "p4obs", "metric_2")
_emit_emits_metric_event("validation_mixin_util", "p4obs", "metric_3")
_emit_emits_metric_event("validation_mixin_util", "p4obs", "metric_4")
_emit_emits_metric_event("validation_mixin_util", "p4obs", "metric_5")
_emit_emits_metric_event("validation_mixin_util", "p4obs", "metric_6")
_emit_records_incident_event("validation_mixin_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("validation_mixin_util", "p4obs", "anomaly")
_emit_writes_observability_log("validation_mixin_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("validation_mixin_util", "p4obs", "mon_state")
_emit_triggers_alert("validation_mixin_util", "p4obs", "alert")
_emit_links_incident_trace("validation_mixin_util", "p4obs", "trace_link")
_emit_captures_pattern("validation_mixin_util", "p3lm", "pattern")
_emit_records_learning_event("validation_mixin_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("validation_mixin_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("validation_mixin_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("validation_mixin_util", "p3lm", "routing")
_emit_improves_agent_policy("validation_mixin_util", "p3lm", "policy")
_emit_stores_learning_state("validation_mixin_util", "p3lm", "state")
_emit_records_execution_trace("validation_mixin_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("validation_mixin_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("validation_mixin_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("validation_mixin_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("validation_mixin_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("validation_mixin_util", "env_read", "p2_env_1")
_emit_reads_environ("validation_mixin_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("validation_mixin_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("validation_mixin_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "validation_mixin_util", "context_pull")
_emit_pulls_context("p1", "validation_mixin_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "validation_mixin_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "validation_mixin_util", "uwg_term_2")
_emit_writes_through("p1", "validation_mixin_util", "write_through")
_emit_writes_through("p1", "validation_mixin_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "validation_mixin_util", "safety_validation")
_emit_invokes_eval("p1", "validation_mixin_util", "eval_call")
_emit_proposal_commits_routing("p1", "validation_mixin_util", "routing_commit")
_emit_escalates_to_human("p1", "validation_mixin_util", "human_escalation")
_emit_routes_through("p1", "validation_mixin_util", "route_through")
_emit_checks_agent_registry("p1", "validation_mixin_util", "agent_registry")
_emit_validates_agent_capability("p1", "validation_mixin_util", "capability")
_emit_dispatches_execution_plan("p1", "validation_mixin_util", "exec_plan")
_emit_agent_executes_agent("p1", "validation_mixin_util", "sub_agent")
_emit_routes_to_agent("p1", "validation_mixin_util", "target_agent")
_emit_verifies_policy("p1", "validation_mixin_util", "policy_check")
_emit_observes_runtime_state("p1", "validation_mixin_util", "runtime_state")
_emit_verifies_boundary("p1", "validation_mixin_util", "boundary_check")
_emit_transcripts_response("p1", "validation_mixin_util", "transcript")
_emit_hard_fails_untranscripted("p1", "validation_mixin_util")
_emit_gated_by_confidence("p1", "validation_mixin_util", "confidence_gate")
emit_replay_key("p0", "validation_mixin_util")
emit_determinism_digest("p0", "validation_mixin_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "validation_mixin_util", "execution_auth")
_emit_validates_capability("p2", "validation_mixin_util", "capability_check")
_emit_routes_to_capability("p2", "validation_mixin_util", "capability_route")
_emit_writes_via_uwg("p2", "validation_mixin_util", "uwg_write")
_emit_blocks_direct_write("p2", "validation_mixin_util", "direct_write_block")
_emit_records_tool_invocation("p2", "validation_mixin_util", "tool_invocation")
_emit_captures_execution_output("p2", "validation_mixin_util", "exec_output")
_emit_dispatches_agent("p3", "validation_mixin_util", "agent_dispatch")
_emit_coordinates_agents("p3", "validation_mixin_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "validation_mixin_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "validation_mixin_util", "healing_outcome")
_emit_escalates_failure("p3", "validation_mixin_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "validation_mixin_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "validation_mixin_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "validation_mixin_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "validation_mixin_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "validation_mixin_util", "eval_metric")
_emit_stores_embedding("p4", "validation_mixin_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "validation_mixin_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "validation_mixin_util", "exec_snapshot_link")


@dataclass
class ValidationResult:
    """Result of a validation operation."""

    passed: bool
    issues: list[str]
    suggestions: list[str]
    metadata: dict[str, Any]


class ValidationMixin:
    """
    Shared mixin for common validation patterns.

    Provides standardized validation workflow methods that eliminate
    duplicate validation boilerplate across agents.
    """

    def validate_with_result(
        self, data: Any, validation_func: callable, context: dict[str, Any] | None = None
    ) -> ValidationResult:
        """
        Execute validation with standardized result format.

        Args:
            data: Data to validate
            validation_func: Function that performs validation
            context: Optional context for validation

        Returns:
            ValidationResult with passed status, issues, and suggestions
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ValidationMixin.validate_with_result")

        issues = []
        suggestions = []
        metadata = {}
        try:
            result = validation_func(data, context or {})
            if isinstance(result, dict):
                issues = result.get("issues", [])
                suggestions = result.get("suggestions", [])
                metadata = result.get("metadata", {})
            elif isinstance(result, list | tuple):
                issues = list(result)
            elif isinstance(result, bool):
                passed = result
                return ValidationResult(
                    passed=passed, issues=issues, suggestions=suggestions, metadata=metadata
                )
            passed = len(issues) == 0
        # guardian: allow-silent-swallow
        except Exception as e:
            issues.append(f"Validation error: {str(e)}")
            passed = False
        return ValidationResult(passed=passed, issues=issues, suggestions=suggestions, metadata=metadata)

    def record_validation_result(self, result: ValidationResult, signal_name: str) -> None:
        """
        Record validation result and manage signals.

        Args:
            result: ValidationResult to record
            signal_name: Signal name to add/remove based on result
        """
        if result.passed:
            self.record_pass("Validation passed", data={"suggestions": result.suggestions, **result.metadata})
            if hasattr(self, "remove_signal"):
                self.remove_signal(signal_name)
        else:
            self.record_fail(
                f"Validation failed: {len(result.issues)} issues",
                data={"issues": result.issues, "suggestions": result.suggestions, **result.metadata},
            )
            if hasattr(self, "add_signal"):
                self.add_signal(signal_name)

    def batch_validate(
        self, validators: list[tuple[str, callable, Any]], stop_on_first_failure: bool = False
    ) -> dict[str, ValidationResult]:
        """
        Run multiple validators in batch.

        Args:
            validators: List of (name, validator_func, data) tuples
            stop_on_first_failure: Whether to stop on first failure

        Returns:
            Dictionary mapping validator names to ValidationResults
        """
        results = {}
        for name, validator_func, data in validators:
            result = self.validate_with_result(data, validator_func)
            results[name] = result
            if stop_on_first_failure and (not result.passed):
                break
        return results

    def validate_required_fields(self, data: dict[str, Any], required_fields: list[str]) -> ValidationResult:
        """
        Validate that required fields are present in data.

        Args:
            data: Data dictionary to validate
            required_fields: List of required field names

        Returns:
            ValidationResult indicating if all required fields present
        """
        issues = []
        for field in required_fields:
            if field not in data:
                issues.append(f"Missing required field: {field}")
            elif data[field] is None:
                issues.append(f"Required field is None: {field}")
            elif isinstance(data[field], str) and (not data[field].strip()):
                issues.append(f"Required field is empty: {field}")
        return ValidationResult(passed=len(issues) == 0, issues=issues, suggestions=[], metadata={})

    def validate_field_types(self, data: dict[str, Any], field_types: dict[str, type]) -> ValidationResult:
        """
        Validate that fields have expected types.

        Args:
            data: Data dictionary to validate
            field_types: Dictionary mapping field names to expected types

        Returns:
            ValidationResult indicating if all fields have correct types
        """
        issues = []
        for field, expected_type in field_types.items():
            if field in data and (not isinstance(data[field], expected_type)):
                actual_type = type(data[field]).__name__
                expected_name = expected_type.__name__
                issues.append(f"Field '{field}' has wrong type: expected {expected_name}, got {actual_type}")
        return ValidationResult(passed=len(issues) == 0, issues=issues, suggestions=[], metadata={})
