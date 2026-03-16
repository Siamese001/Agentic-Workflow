"""
Shared Validation Mixin - Phase 2 Optimization
Provides common validation workflow patterns for agents.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "validation_mixin_util", "p0_governance")
_emit_reads_policy_state("p0", "validation_mixin_util", "policy_binding")
_emit_snapshots_state("p0", "validation_mixin_util", "state_snapshot")
emit_replay_key("p0", "validation_mixin_util")
emit_determinism_digest("p0", "validation_mixin_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


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
