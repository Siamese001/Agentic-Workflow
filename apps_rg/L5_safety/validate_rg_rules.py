# Ownership: apps_rg / L5_safety
# -*- coding: utf-8 -*-
"""Validation engine for resume generation."""

from __future__ import annotations

from typing import Dict, List, Optional

from shared.models import ValidationResult, ValidationSeverity
from apps_rg.L5_safety.define_validation_rule import ValidationRule


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

    def has_critical_failures(self, results: List[ValidationResult]) -> bool:
        """Check if any critical failures exist."""
        return any(not r.passed and r.severity == ValidationSeverity.CRITICAL for r in results)
