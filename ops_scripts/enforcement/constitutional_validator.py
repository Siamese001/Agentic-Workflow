"""
ConstitutionalValidator - Deterministic enforcement of constitutional rules.

Pure deterministic logic only. No side effects, no dynamic imports, no filesystem writes.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Immutable validation result with deterministic representation."""

    is_valid: bool
    violations: tuple[str, ...] = ()

    def __repr__(self) -> str:
        """Deterministic repr without timestamps or UUIDs."""
        violations_str = ", ".join(f"'{v}'" for v in self.violations)
        return f"ValidationResult(is_valid={self.is_valid}, violations=[{violations_str}])"


def _result(violations: list[str]) -> ValidationResult:
    return ValidationResult(is_valid=not violations, violations=tuple(violations))


def _require_mapping(payload: object, payload_name: str) -> tuple[Mapping[str, object] | None, list[str]]:
    if isinstance(payload, Mapping):
        return payload, []
    return None, [f"{payload_name} must be a mapping"]


class ConstitutionalValidator:
    """Deterministic validator for constitutional compliance."""

    def validate_phase_execution(self, phase_data: object) -> ValidationResult:
        """
        Validate phase execution follows constitutional rules.

        Required keys:
        - "phase_id": str
        - "evidence_files": list[str]

        Rules:
        - Exactly one evidence file required
        - All required keys must be present
        """
        payload, violations = _require_mapping(phase_data, "phase_data")
        if violations:
            return _result(violations)

        required_keys = ["phase_id", "evidence_files"]
        for key in required_keys:
            if key not in payload:
                violations.append(f"Missing required key: {key}")
        if violations:
            return _result(violations)

        phase_id = payload["phase_id"]
        evidence_files = payload["evidence_files"]

        if not isinstance(phase_id, str) or not phase_id.strip():
            violations.append("phase_id must be a non-empty str")

        if not isinstance(evidence_files, Sequence) or isinstance(evidence_files, (str, bytes)):
            violations.append("evidence_files must be a sequence of strings")
        elif len(evidence_files) != 1:
            violations.append(f"Exactly 1 evidence file required, found {len(evidence_files)}")
        elif not isinstance(evidence_files[0], str) or not evidence_files[0].strip():
            violations.append("evidence_files[0] must be a non-empty str")

        return _result(violations)

    def validate_stop_at_criteria(self, execution_result: object) -> ValidationResult:
        """
        Validate stop-at-acceptance criteria.

        Required keys:
        - "acceptance_met": bool
        - "continued_execution": bool

        Rules:
        - If acceptance_met is True, continued_execution must be False
        - All required keys must be present
        """
        payload, violations = _require_mapping(execution_result, "execution_result")
        if violations:
            return _result(violations)

        required_keys = ["acceptance_met", "continued_execution"]
        for key in required_keys:
            if key not in payload:
                violations.append(f"Missing required key: {key}")
        if violations:
            return _result(violations)

        acceptance_met = payload["acceptance_met"]
        continued_execution = payload["continued_execution"]

        if not isinstance(acceptance_met, bool):
            violations.append("acceptance_met must be a bool")
        if not isinstance(continued_execution, bool):
            violations.append("continued_execution must be a bool")
        if any("must be a bool" in v for v in violations):
            return _result(violations)
        if acceptance_met and continued_execution:
            violations.append("Execution continued after acceptance met")
        return _result(violations)
