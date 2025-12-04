# File: validation/validation_engine.py
# Validation Engine Module - V18 Architecture
# Version: 18.00
# Contains the core validation engine, rule, and classifier classes.
# Refactored from validator_RES_v3_8.py

import logging
from typing import Dict, List, Optional, Any, Callable, Union
from collections import defaultdict
from models_RES import ValidationResult, ValidationSeverity


class ValidationRule:
    """
    Represents a single executable validation rule.
    (Extracted from resume_workflow_v16_20.py)
    """
    def __init__(self, rule_id: str, severity: ValidationSeverity, validator: Any, error_message: Union[str, Callable[[Dict], str]], category: str = "general"):
        self.rule_id = rule_id
        self.severity = severity
        self.validator = validator
        self.error_message = error_message
        self.category = category

    def execute(self, data: Dict) -> ValidationResult:
        """
        Executes the validation rule against the provided data.
        Now accepts both Dict and ValidationContext for full v16_20 compatibility.
        """
        try:
            # The validator function is called with the data/context
            passed = self.validator(data)

            error_msg = ""
            if not passed:
                if callable(self.error_message):
                    # The error message lambda is also called with the data/context
                    error_msg = self.error_message(data)
                else:
                    error_msg = self.error_message

            # Handle both Dict and ValidationContext for details
            # This matches monolithic v16_20 behavior exactly
            if isinstance(data, dict):
                details = data.get('error_details', {})
            else:
                # ValidationContext object
                try:
                    details = data.get_details_for_rule(self.rule_id)
                except AttributeError:
                    details = {}

            return ValidationResult(
                rule_id=self.rule_id,
                passed=passed,
                severity=self.severity,
                message=error_msg,
                details=details
            )
        except Exception as e:
            return ValidationResult(
                rule_id=self.rule_id,
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                message=f"Validation logic failed for {self.rule_id}: {str(e)}",
                details={'exception': str(e)}
            )


class ValidationEngine:
    """
    Manages the registration and execution of validation rules.
    (Extracted from resume_workflow_v16_20.py)
    """
    def __init__(self):
        self.rules: List[ValidationRule] = []
        self.rules_by_category: Dict[str, List[ValidationRule]] = defaultdict(list)

    def register_rule(self, rule: ValidationRule) -> None:
        """Registers a single validation rule."""
        self.rules.append(rule)
        self.rules_by_category[rule.category].append(rule)

    def register_rules(self, rules: List[ValidationRule]) -> None:
        """Registers a list of validation rules."""
        for rule in rules:
            self.register_rule(rule)

    def validate(self, data: 'ValidationContext', categories: Optional[List[str]] = None) -> List[ValidationResult]:
        """
        Validates the data against registered rules.
        """
        results = []

        rules_to_run = self.rules
        if categories:
            rules_to_run = []
            for category in categories:
                rules_to_run.extend(self.rules_by_category.get(category, []))

        for rule in rules_to_run:
            result = rule.execute(data)
            results.append(result)

        return results

    def has_high_or_critical_failures(self, results: List[ValidationResult]) -> bool:
        """Checks if any high or critical failures are present."""
        return any(
            not r.passed and r.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.HIGH]
            for r in results
        )


class ConstraintFailureClassifier:
    """
    Classifies validation failures to inform retry strategies.
    (Extracted from resume_workflow_v16_20.py)
    """
    @staticmethod
    def classify_failure(
        validation_result: ValidationResult,
        original_temperature: float
    ) -> str:
        """
        Returns failure category to determine optimal retry approach:
        - "MECHANICAL": Word count, format, structure (lower temp helps)
        - "CREATIVE": Placeholders, generic content (higher temp needed)
        - "SEMANTIC": Forbidden verbs, intro phrases (prompt changes help)
        - "CONFLICT": Impossible constraint combination (needs redesign)
        """
        rule_id = validation_result.rule_id
        
        if any(keyword in rule_id for keyword in ["WORD_COUNT", "SENTENCE_COUNT", "FORMAT", "STRUCTURE"]):
            return "MECHANICAL"
        
        if any(keyword in rule_id for keyword in ["PLACEHOLDER", "GENERIC", "MOCK", "EMPTY"]):
            return "CREATIVE"
        
        if any(keyword in rule_id for keyword in ["FORBIDDEN_VERB", "INTRO_PHRASE", "NO_", "INVALID_"]):
            return "SEMANTIC"
        
        if original_temperature <= 0.4 and not validation_result.passed:
            return "CONFLICT"
        
        return "UNKNOWN"