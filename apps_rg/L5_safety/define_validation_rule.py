# Ownership: apps_rg / L5_safety
# -*- coding: utf-8 -*-
"""Validation rule definition for resume generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Union

from shared.models import ValidationResult, ValidationSeverity


@dataclass
class ValidationRule:
    """Single validation rule with callable validator."""

    rule_id: str
    severity: ValidationSeverity
    validator: Callable[[Dict], bool]
    error_message: Union[str, Callable[[Dict], str]]
    category: str = "general"

    def execute(self, data: Dict) -> ValidationResult:
        """Execute validation rule and return result."""
        try:
            passed = self.validator(data)
            error_msg = ""
            if not passed:
                if callable(self.error_message):
                    error_msg = self.error_message(data)
                else:
                    error_msg = self.error_message

            return ValidationResult(
                rule_id=self.rule_id,
                passed=passed,
                severity=self.severity,
                message=error_msg,
                details=data.get("error_details", {}),
            )
        except Exception as e:
            return ValidationResult(
                rule_id=self.rule_id,
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                message=f"Validation logic failed for {self.rule_id}: {e}",
                details={"exception": str(e)},
            )
