"""
validation.py - Shared Execution Module.

This module provides the core implementation for Validation, handling
standardized execution flows, error management, and context propagation
within the shared application layer.
"""

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Standardized operation result container."""

    success: bool
    data: str | int | float | bool | list | dict | None = None
    metadata: dict[str, str | int | float | bool | list | dict] = field(default_factory=dict)
    error_message: str | None = None


class Validation:
    """
    Executor for shared validation operations.

    Ensures consistent handling of configuration context and error boundaries
    across the sovereign domain.
    """

    def __init__(self, config: dict[str, str | int | float | bool | list | dict] | None = None):
        self.config = config or {}
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def process(
        self,
        payload: str | int | float | bool | list | dict,
        context: dict | None = None,
    ) -> ExecutionResult:
        """
        Execute the primary logic for this module.

        Args:
            payload: The input data to process
            context: Optional execution context

        Returns:
            ExecutionResult indicating success or failure
        """
        try:
            self._logger.info("Starting processing execution")
            result = self._execute_logic(payload, context)
            return ExecutionResult(success=True, data=result)
        except (ValueError, TypeError, KeyError) as e:
            self._logger.error(f"Validation error during processing: {e}")
            return ExecutionResult(success=False, error_message=str(e))
        except Exception as e:
            self._logger.error(f"Unexpected system error: {e}", exc_info=True)
            return ExecutionResult(success=False, error_message="Internal System Error")

    def _execute_logic(
        self,
        data: str | int | float | bool | list | dict,
        context: dict | None,
    ) -> str | int | float | bool | list | dict:
        """Internal validation logic implementation."""
        validation_result = {"is_valid": True, "errors": [], "warnings": [], "validated_data": data}
        if isinstance(data, dict):
            validation_result = self._validate_dict(data, validation_result)
        elif isinstance(data, list):
            validation_result = self._validate_list(data, validation_result)
        elif isinstance(data, str):
            validation_result = self._validate_string(data, validation_result)
        elif isinstance(data, int | float):
            validation_result = self._validate_number(data, validation_result)
        elif isinstance(data, bool):
            validation_result = self._validate_boolean(data, validation_result)
        if context:
            validation_result["context"] = {
                "validation_context": context,
                "validation_timestamp": self._get_timestamp(),
            }
        return validation_result

    def _validate_dict(self, data: dict, result: dict) -> dict:
        """Validate dictionary data."""
        required_fields = self.config.get("required_fields", [])
        for field in required_fields:
            if field not in data:
                result["errors"].append(f"Missing required field: {field}")
                result["is_valid"] = False
        field_types = self.config.get("field_types", {})
        for field, expected_type in field_types.items():
            if field in data:
                if not isinstance(data[field], expected_type):
                    result["errors"].append(
                        f"Field '{field}' must be of type {expected_type.__name__}, got {type(data[field]).__name__}",
                    )
                    result["is_valid"] = False
        return result

    def _validate_list(self, data: list, result: dict) -> dict:
        """Validate list data."""
        max_length = self.config.get("max_list_length", 100)
        min_length = self.config.get("min_list_length", 0)
        if len(data) > max_length:
            result["errors"].append(f"List exceeds maximum length of {max_length}")
            result["is_valid"] = False
        if len(data) < min_length:
            result["errors"].append(f"List below minimum length of {min_length}")
            result["is_valid"] = False
        item_type = self.config.get("list_item_type")
        if item_type:
            for i, item in enumerate(data):
                if not isinstance(item, item_type):
                    result["errors"].append(
                        f"List item at index {i} must be of type {item_type.__name__}, got {type(item).__name__}",
                    )
                    result["is_valid"] = False
        return result

    def _validate_string(self, data: str, result: dict) -> dict:
        """Validate string data."""
        max_length = self.config.get("max_string_length", 1000)
        min_length = self.config.get("min_string_length", 0)
        if len(data) > max_length:
            result["errors"].append(f"String exceeds maximum length of {max_length}")
            result["is_valid"] = False
        if len(data) < min_length:
            result["errors"].append(f"String below minimum length of {min_length}")
            result["is_valid"] = False
        pattern = self.config.get("string_pattern")
        if pattern:
            import re

            if not re.match(pattern, data):
                result["errors"].append(f"String does not match required pattern: {pattern}")
                result["is_valid"] = False
        return result

    def _validate_number(self, data: int | float, result: dict) -> dict:
        """Validate numeric data."""
        min_value = self.config.get("min_value")
        max_value = self.config.get("max_value")
        if min_value is not None and data < min_value:
            result["errors"].append(f"Value {data} is below minimum {min_value}")
            result["is_valid"] = False
        if max_value is not None and data > max_value:
            result["errors"].append(f"Value {data} is above maximum {max_value}")
            result["is_valid"] = False
        return result

    def _validate_boolean(self, data: bool, result: dict) -> dict:
        """Validate boolean data."""
        return result

    def _get_timestamp(self) -> str:
        """Get current timestamp for validation context."""
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()


def run_process(data: str | int | float | bool | list | dict) -> ExecutionResult:
    """Module-level entry point."""
    executor = Validation()
    return executor.process(data)
