"""
ConstitutionalValidator - Deterministic enforcement of constitutional rules.

Pure deterministic logic only. No side effects, no dynamic imports, no filesystem writes.
"""

from dataclasses import dataclass

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)


@dataclass(frozen=True)
class ValidationResult:
    """Immutable validation result with deterministic representation."""

    is_valid: bool
    violations: list[str]

    def __repr__(self) -> str:
        """Deterministic repr without timestamps or UUIDs."""
        violations_str = ", ".join(f"'{v}'" for v in self.violations)
        return f"ValidationResult(is_valid={self.is_valid}, violations=[{violations_str}])"


class ConstitutionalValidator:
    """Deterministic validator for constitutional compliance."""

    def validate_phase_execution(self, phase_data: dict) -> ValidationResult:
        """
        Validate phase execution follows constitutional rules.

        Required keys:
        - "phase_id": str
        - "evidence_files": list[str]

        Rules:
        - Exactly one evidence file required
        - All required keys must be present
        """
        violations = []
        required_keys = ["phase_id", "evidence_files"]
        for key in required_keys:
            if key not in phase_data:
                violations.append(f"Missing required key: {key}")
        if violations:
            return ValidationResult(is_valid=False, violations=violations)
        evidence_files = phase_data["evidence_files"]
        if not isinstance(evidence_files, list):
            violations.append("evidence_files must be a list")
        elif len(evidence_files) != 1:
            violations.append(f"Exactly 1 evidence file required, found {len(evidence_files)}")
        return ValidationResult(is_valid=len(violations) == 0, violations=violations)

    def validate_stop_at_criteria(self, execution_result: dict) -> ValidationResult:
        """
        Validate stop-at-acceptance criteria.

        Required keys:
        - "acceptance_met": bool
        - "continued_execution": bool

        Rules:
        - If acceptance_met is True, continued_execution must be False
        - All required keys must be present
        """
        violations = []
        required_keys = ["acceptance_met", "continued_execution"]
        for key in required_keys:
            if key not in execution_result:
                violations.append(f"Missing required key: {key}")
        if violations:
            return ValidationResult(is_valid=False, violations=violations)
        acceptance_met = execution_result["acceptance_met"]
        continued_execution = execution_result["continued_execution"]
        if not isinstance(acceptance_met, bool):
            violations.append("acceptance_met must be a bool")
        if not isinstance(continued_execution, bool):
            violations.append("continued_execution must be a bool")
        if any("must be a bool" in v for v in violations):
            return ValidationResult(is_valid=False, violations=violations)
        if acceptance_met and continued_execution:
            violations.append("Execution continued after acceptance met")
        return ValidationResult(is_valid=len(violations) == 0, violations=violations)
