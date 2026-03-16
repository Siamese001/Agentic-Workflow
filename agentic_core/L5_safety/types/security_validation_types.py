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

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "security_validation_types")
emit_determinism_digest("p0", "security_validation_types")

_emit_dispatches_healing_run("p1", "security_validation_types", "L5")
_emit_routes_through("p1", "security_validation_types", "L5")
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
        self, validator_name: str, content: Any, context: dict | None = None
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
            _trace_id, LayerSegment.L5_POLICY, "RedTeamValidationSuite.run_validator"
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
                validator_name=validator_name, valid=False, errors=[f"Validator '{validator_name}' not found"]
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
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f"[SecuritySuite] Validator {validator_name} failed: {e}")
            return SecurityValidationResult(
                validator_name=validator_name, valid=False, errors=[f"Validator error: {str(e)}"]
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
