"""
check_scripts_compliance.py - Validation Module

Domain: utilities
Generated: 2025-12-07T12:07:59.873366
"""

import logging
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, field

LOGGER = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """TODO: Add docstring."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class ValidationFinding:
    """A validation finding."""
    code: str
    message: str
    severity: ValidationSeverity
    path: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of validation."""
    is_valid: bool
    findings: List[ValidationFinding] = field(default_factory=list)

    @property
    def errors(self) -> List[ValidationFinding]:
        """Docstring."""
        return [f for f in self.findings if f.severity == ValidationSeverity.ERROR]


class CheckScriptsCompliance:
    """Validator for utilities domain."""

    def __init__(self, config: Optional[Dict[str, object]] = None):
        self.config = config or {}
        self.strict = self.config.get("strict", False)
        logger.info(f"Initialized {self.__class__.__name__}")

    def validate(self, data: object, schema: Optional[Dict] = None) -> ValidationResult:
        """Validate data against schema."""
        findings = []
        findings.extend(self._validate_types(data, schema))
        findings.extend(self._validate_required(data, schema))

        is_valid = not any(
            f.severity == ValidationSeverity.ERROR for f in findings)
        return ValidationResult(is_valid=is_valid, findings=findings)

    def _validate_types(self, data: object, schema: Optional[Dict]) -> List[ValidationFinding]:
        """Validate data types."""
        findings = []
        if schema and "type" in schema:
            expected = schema["type"]
            actual = type(data).__name__
            if expected != actual:
                findings.append(ValidationFinding(
                    code="TYPE_MISMATCH",
                    message=f"Expected {expected}, got {actual}",
                    severity=ValidationSeverity.ERROR
                ))
        return findings

    def _validate_required(self, data: object, schema: Optional[Dict]) -> List[ValidationFinding]:
        """Validate required fields."""
        findings = []
        if schema and "required" in schema and isinstance(data, dict):
            for field in schema["required"]:
                if field not in data:
                    findings.append(ValidationFinding(
                        code="MISSING_REQUIRED",
                        message=f"Missing: {field}",
                        severity=ValidationSeverity.ERROR,
                        path=field
                    ))
        return findings


def validate(data: object,
             schema: Optional[Dict] = None,
             config: Optional[Dict] = None) -> ValidationResult:
    """Convenience function for validation."""
    return CheckScriptsCompliance(config).validate(data, schema)

