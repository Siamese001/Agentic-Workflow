"""
Validation Engine Implementation
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ValidationResult:
    """Result from validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    validated_data: Any = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class Validation:
    """Engine for validating tool inputs and outputs"""

    def __init__(self):
        self.validation_history: List[Dict[str, Any]] = []
        self.validation_rules = {}

    def add_rule(self, rule_name: str, rule_func):
        """Add a validation rule"""
        self.validation_rules[rule_name] = rule_func

    def validate_input(self, tool_name: str, input_data: Dict[str, Any]) -> ValidationResult:
        """Validate input data for a tool"""
        errors = []
        warnings = []

        # Basic validation
        if not isinstance(input_data, dict):
            errors.append("Input data must be a dictionary")

        if not input_data:
            warnings.append("Input data is empty")

        # Apply specific rules if they exist
        rule_key = f"{tool_name}_input"
        if rule_key in self.validation_rules:
            try:
                rule_result = self.validation_rules[rule_key](input_data)
                if isinstance(rule_result, dict):
                    errors.extend(rule_result.get("errors", []))
                    warnings.extend(rule_result.get("warnings", []))
            except Exception as e:
                errors.append(f"Validation rule error: {str(e)}")

        result = ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            validated_data=input_data
        )

        self.validation_history.append({
            "tool_name": tool_name,
            "validation_type": "input",
            "input_data": input_data,
            "result": result,
            "timestamp": datetime.now()
        })

        return result

    def validate_output(self, tool_name: str, output_data: Any) -> ValidationResult:
        """Validate output data from a tool"""
        errors = []
        warnings = []

        # Basic validation
        if output_data is None:
            warnings.append("Output data is None")

        # Apply specific rules if they exist
        rule_key = f"{tool_name}_output"
        if rule_key in self.validation_rules:
            try:
                rule_result = self.validation_rules[rule_key](output_data)
                if isinstance(rule_result, dict):
                    errors.extend(rule_result.get("errors", []))
                    warnings.extend(rule_result.get("warnings", []))
            except Exception as e:
                errors.append(f"Validation rule error: {str(e)}")

        result = ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            validated_data=output_data
        )

        self.validation_history.append({
            "tool_name": tool_name,
            "validation_type": "output",
            "output_data": output_data,
            "result": result,
            "timestamp": datetime.now()
        })

        return result

    def get_validation_history(self) -> List[Dict[str, Any]]:
        """Get validation history"""
        return self.validation_history.copy()

    def clear_history(self):
        """Clear validation history"""
        self.validation_history.clear()
