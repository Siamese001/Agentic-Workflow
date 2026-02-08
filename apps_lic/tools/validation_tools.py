"""
Validation tools for LIC domain.

Provides schema validation utilities used by validator agents.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValidationResult:
    """Result of a validation operation."""

    is_valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_error(self, error: str) -> None:
        """Add an error and mark as invalid."""
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

    if not isinstance(data, dict):
        result.add_error("Data must be a dictionary")
        return result

    # Basic validation - check required fields if schema provided
    if schema:
        required = schema.get("required", [])
        for req_field in required:
            if req_field not in data:
                result.add_error(f"Missing required field: {req_field}")

    return result


__all__ = ["ValidationResult", "validate_schema_policy"]
