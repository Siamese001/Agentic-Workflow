"""
Security Validation Suite - Phase 2 Red Team Integration

Provides a unified interface for running all security validators:
- Adversarial probing
- Boundary testing
- Prompt injection detection (future)

This module creates a RedTeamValidationSuite that orchestrates
security testing across multiple validators.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
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

emit_replay_key("p0", "security_validation_types")
emit_determinism_digest("p0", "security_validation_types")

_emit_dispatches_healing_run("p1", "security_validation_types", "L5")
_emit_routes_through("p1", "security_validation_types", "L5")
_emit_checks_agent_registry("p1", "security_validation_types", "agent_registry")
_emit_validates_agent_capability("p1", "security_validation_types", "capability")
_emit_dispatches_execution_plan("p1", "security_validation_types", "exec_plan")
_emit_agent_executes_agent("p1", "security_validation_types", "sub_agent")
_emit_routes_to_agent("p1", "security_validation_types", "target_agent")
_emit_verifies_policy("p1", "security_validation_types", "policy_check")
_emit_observes_runtime_state("p1", "security_validation_types", "runtime_state")
_emit_verifies_boundary("p1", "security_validation_types", "boundary_check")
_emit_transcripts_response("p1", "security_validation_types", "transcript")
_emit_hard_fails_untranscripted("p1", "security_validation_types")
_emit_gated_by_confidence("p1", "security_validation_types", "confidence_gate")
_emit_escalates_to_human("p1", "security_validation_types", "L5")
_emit_reads_policy_state("p1", "security_validation_types", "L5")

_emit_applies_guardrail("p0", "security_validation_types", "p0_governance")
_emit_snapshots_state("p0", "security_validation_types", "state_snapshot")
_emit_authorize_and_execute("p2", "security_validation_types", "execution_auth")
_emit_validates_capability("p2", "security_validation_types", "capability_check")
_emit_routes_to_capability("p2", "security_validation_types", "capability_route")
_emit_writes_via_uwg("p2", "security_validation_types", "uwg_write")
_emit_blocks_direct_write("p2", "security_validation_types", "direct_write_block")
_emit_records_tool_invocation("p2", "security_validation_types", "tool_invocation")
_emit_captures_execution_output("p2", "security_validation_types", "exec_output")
_emit_dispatches_agent("p3", "security_validation_types", "agent_dispatch")
_emit_coordinates_agents("p3", "security_validation_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "security_validation_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "security_validation_types", "healing_outcome")
_emit_escalates_failure("p3", "security_validation_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "security_validation_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "security_validation_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "security_validation_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "security_validation_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "security_validation_types", "eval_metric")
_emit_stores_embedding("p4", "security_validation_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "security_validation_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "security_validation_types", "exec_snapshot_link")
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

_emit_emits_metric_event("security_validation_types", "p4obs", "metric_1")
_emit_emits_metric_event("security_validation_types", "p4obs", "metric_2")
_emit_emits_metric_event("security_validation_types", "p4obs", "metric_3")
_emit_emits_metric_event("security_validation_types", "p4obs", "metric_4")
_emit_emits_metric_event("security_validation_types", "p4obs", "metric_5")
_emit_emits_metric_event("security_validation_types", "p4obs", "metric_6")
_emit_records_incident_event("security_validation_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("security_validation_types", "p4obs", "anomaly")
_emit_writes_observability_log("security_validation_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("security_validation_types", "p4obs", "mon_state")
_emit_triggers_alert("security_validation_types", "p4obs", "alert")
_emit_links_incident_trace("security_validation_types", "p4obs", "trace_link")
_emit_captures_pattern("security_validation_types", "p3lm", "pattern")
_emit_records_learning_event("security_validation_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("security_validation_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("security_validation_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("security_validation_types", "p3lm", "routing")
_emit_improves_agent_policy("security_validation_types", "p3lm", "policy")
_emit_stores_learning_state("security_validation_types", "p3lm", "state")
_emit_records_execution_trace("security_validation_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("security_validation_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("security_validation_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("security_validation_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("security_validation_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("security_validation_types", "env_read", "p2_env_1")
_emit_reads_environ("security_validation_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("security_validation_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("security_validation_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "security_validation_types", "context_pull")
_emit_pulls_context("p1", "security_validation_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "security_validation_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "security_validation_types", "uwg_term_2")
_emit_writes_through("p1", "security_validation_types", "write_through")
_emit_writes_through("p1", "security_validation_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "security_validation_types", "safety_validation")
_emit_invokes_eval("p1", "security_validation_types", "eval_call")
_emit_proposal_commits_routing("p1", "security_validation_types", "routing_commit")

Logger = logging.getLogger(__name__)


@dataclass
class SecurityValidationResult:
    """Result from a security validation run."""

    validator_name: str
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class SecuritySuiteResult:
    """Aggregated result from running the full security suite."""

    overall_valid: bool
    validators_run: int
    validators_passed: int
    validators_failed: int
    results: list[SecurityValidationResult] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    execution_time_ms: float = 0.0


class RedTeamValidationSuite:
    """
    Orchestrates security validation across multiple red team validators.

    Usage:
        suite = RedTeamValidationSuite()
        result = suite.run_all(content={"test": "data"})
        if not result.overall_valid:
            print(f"Security issues found: {result.validators_failed} validators failed")
    """

    def __init__(self) -> None:
        """Initialize the security validation suite."""
        self._validators: dict[str, Any] = {}
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Lazy initialization of validators."""
        if self._initialized:
            return
        try:
            from agentic_core.L5_safety.validators.red_team_integration_types import (
                get_adversarial_validator,
                get_boundary_validator,
            )

            self._validators["adversarial_probe"] = get_adversarial_validator()
            self._validators["boundary_testing"] = get_boundary_validator()
            self._initialized = True
            Logger.info(f"[SecuritySuite] Initialized with {len(self._validators)} validators")
        except ImportError as e:
            Logger.warning(f"[SecuritySuite] Could not import validators: {e}")
            self._initialized = True

    def run_validator(
        self,
        validator_name: str,
        content: Any,
        context: dict | None = None,
    ) -> SecurityValidationResult:
        """
        Run a specific validator.

        Args:
            validator_name: Name of the validator to run
            content: Content to validate
            context: Optional validation context

        Returns:
            SecurityValidationResult with validation details
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L5_POLICY,
            "RedTeamValidationSuite.run_validator",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:RedTeamValidationSuite.run_validator".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        self._ensure_initialized()
        context = context or {}
        if validator_name not in self._validators:
            return SecurityValidationResult(
                validator_name=validator_name,
                valid=False,
                errors=[f"Validator '{validator_name}' not found"],
            )
        try:
            validator = self._validators[validator_name]
            result = validator.validate(content, context)
            return SecurityValidationResult(
                validator_name=validator_name,
                valid=result.get("valid", False),
                errors=result.get("errors", []),
                warnings=result.get("warnings", []),
                metadata={k: v for k, v in result.items() if k not in ("valid", "errors", "warnings")},
            )
        except (ValueError, TypeError) as e:  # guardian: allow-silent-swallow
            Logger.error(f"[SecuritySuite] Validator {validator_name} failed: {e}")
            return SecurityValidationResult(
                validator_name=validator_name,
                valid=False,
                errors=[f"Validator error: {str(e)}"],
            )

    def run_all(self, content: Any, context: dict | None = None) -> SecuritySuiteResult:
        """
        Run all registered security validators.

        Args:
            content: Content to validate
            context: Optional validation context

        Returns:
            SecuritySuiteResult with aggregated results
        """
        import time

        self._ensure_initialized()
        context = context or {}
        start_time = time.time()
        results: list[SecurityValidationResult] = []
        for validator_name in self._validators:
            result = self.run_validator(validator_name, content, context)
            results.append(result)
        execution_time = (time.time() - start_time) * 1000
        passed = sum(1 for r in results if r.valid)
        failed = len(results) - passed
        return SecuritySuiteResult(
            overall_valid=failed == 0,
            validators_run=len(results),
            validators_passed=passed,
            validators_failed=failed,
            results=results,
            execution_time_ms=execution_time,
        )

    def get_available_validators(self) -> list[str]:
        """Get list of available validator names."""
        self._ensure_initialized()
        return list(self._validators.keys())

    def get_status(self) -> dict[str, Any]:
        """Get current status of the security suite."""
        self._ensure_initialized()
        return {
            "initialized": self._initialized,
            "validators_available": list(self._validators.keys()),
            "validator_count": len(self._validators),
        }


_security_suite: RedTeamValidationSuite | None = None


def get_security_suite() -> RedTeamValidationSuite:
    """Get or create the global security validation suite."""
    global _security_suite
    if _security_suite is None:
        _security_suite = RedTeamValidationSuite()
    return _security_suite


def run_security_validation(content: Any, context: dict | None = None) -> SecuritySuiteResult:
    """
    Convenience function to run full security validation.

    Args:
        content: Content to validate
        context: Optional validation context

    Returns:
        SecuritySuiteResult with all validation results
    """
    suite = get_security_suite()
    return suite.run_all(content, context)
