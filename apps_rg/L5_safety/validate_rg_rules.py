# Ownership: apps_rg / L5_safety
# Layer: L5_safety
# Agent: apps_rg
# -*- coding: utf-8 -*-
"""
Validation rule engine for resume generation.

Provides ValidationRule class and ValidationEngine for rule-based validation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union

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


class ValidationEngine:
    """Unified validation engine with rule registry pattern."""

    def __init__(self) -> None:
        """Initialize the validation engine."""
        self.rules: List[ValidationRule] = []
        self.rules_by_category: Dict[str, List[ValidationRule]] = {}

    def register_rule(self, rule: ValidationRule) -> None:
        """Register a validation rule."""
        self.rules.append(rule)
        if rule.category not in self.rules_by_category:
            self.rules_by_category[rule.category] = []
        self.rules_by_category[rule.category].append(rule)

    def register_rules(self, rules: List[ValidationRule]) -> None:
        """Register multiple validation rules."""
        for rule in rules:
            self.register_rule(rule)

    def validate(
        self, data: Dict, categories: Optional[List[str]] = None
    ) -> List[ValidationResult]:
        """Run validation rules and return results."""
        rules_to_run = self.rules
        if categories:
            rules_to_run = []
            for category in categories:
                rules_to_run.extend(self.rules_by_category.get(category, []))

        return [rule.execute(data) for rule in rules_to_run]

    def get_failed_validations(
        self, results: List[ValidationResult]
    ) -> List[ValidationResult]:
        """Filter to only failed validations."""
        return [r for r in results if not r.passed]

    def has_critical_failures(self, results: List[ValidationResult]) -> bool:
        """Check if any critical failures exist."""
        return any(
            not r.passed and r.severity == ValidationSeverity.CRITICAL for r in results
        )
