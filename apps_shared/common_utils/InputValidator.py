"""Input Validator - Comprehensive validation beyond prompt injection.

This module provides schema-based validation, type safety, and protection
against malformed data, JSON/XML attacks, and boundary violations.
"""

import json
import logging
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ValidationError, validator

logger = logging.getLogger(__name__)


class ValidationType(Enum):
    """Types of validation."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"
    DATETIME = "datetime"
    JSON = "json"
    XML = "xml"
    REGEX = "regex"
    CUSTOM = "custom"


@dataclass
class ValidationRule:
    """Rule for validating input."""
    name: str
    validation_type: ValidationType
    required: bool = True
    min_length: int | None = None
    max_length: int | None = None
    min_value: int | float | None = None
    max_value: int | float | None = None
    pattern: str | None = None
    allowed_values: list[Any] | None = None
    schema: dict[str, Any] | None = None
    custom_validator: callable | None = None
    sanitize: bool = True


class InputValidationError(Exception):
    """Raised when input validation fails."""

    def __init__(self, field: str, message: str, value: Any = None):
        """Initialize validation error.

        Args:
            field: Field that failed validation
            message: Error message
            value: Value that failed
        """
        self.field = field
        self.message = message
        self.value = value
        super().__init__(f"Validation failed for {field}: {message}")


class InputValidator:
    """Validates input data against schema and rules."""

    def __init__(self, name: str = "default"):
        """Initialize the validator.

        Args:
            name: Validator name for logging
        """
        self.name = name
        self._rules: dict[str, ValidationRule] = {}
        self._schemas: dict[str, dict[str, Any]] = {}

        logger.debug(f"Initialized InputValidator: {name}")

    def add_rule(self, field: str, rule: ValidationRule) -> None:
        """Add a validation rule.

        Args:
            field: Field name
            rule: Validation rule
        """
        self._rules[field] = rule
        logger.debug(f"Added validation rule for field: {field}")

    def add_schema(self, schema_name: str, schema: dict[str, Any]) -> None:
        """Add a JSON schema.

        Args:
            schema_name: Name for the schema
            schema: JSON schema dictionary
        """
        self._schemas[schema_name] = schema
        logger.debug(f"Added schema: {schema_name}")

    def validate(self, data: dict[str, Any], strict: bool = True) -> dict[str, Any]:
        """Validate input data.

        Args:
            data: Input data to validate
            strict: Whether to raise errors for unknown fields

        Returns:
            Validated and sanitized data

        Raises:
            InputValidationError: If validation fails
        """
        validated = {}
        errors = []

        # Check all rules
        for field, rule in self._rules.items():
            try:
                value = data.get(field)

                # Check required
                if rule.required and value is None:
                    raise InputValidationError(field, "Field is required")

                # Skip validation if not required and value is None
                if value is None and not rule.required:
                    continue

                # Validate based on type
                validated_value = self._validate_field(field, value, rule)
                validated[field] = validated_value

            except InputValidationError as e:
                errors.append(e)

        # Check for unknown fields in strict mode
        if strict:
            for field in data:
                if field not in self._rules:
                    logger.warning(f"Unknown field in input: {field}")

        # Raise errors if any
        if errors:
            error_messages = [f"{e.field}: {e.message}" for e in errors]
            raise InputValidationError("multiple", f"Validation failed: {', '.join(error_messages)}")

        return validated

    def _validate_field(self, field: str, value: Any, rule: ValidationRule) -> Any:
        """Validate a single field.

        Args:
            field: Field name
            value: Field value
            rule: Validation rule

        Returns:
            Validated and sanitized value

        Raises:
            InputValidationError: If validation fails
        """
        # Type validation
        validated_value = self._validate_type(value, rule)

        # Length validation
        if rule.min_length is not None:
            if isinstance(validated_value, (str, list, dict)):
                if len(validated_value) < rule.min_length:
                    raise InputValidationError(field, f"Minimum length is {rule.min_length}")

        if rule.max_length is not None:
            if isinstance(validated_value, (str, list, dict)):
                if len(validated_value) > rule.max_length:
                    raise InputValidationError(field, f"Maximum length is {rule.max_length}")

        # Value validation
        if rule.min_value is not None:
            if isinstance(validated_value, (int, float)):
                if validated_value < rule.min_value:
                    raise InputValidationError(field, f"Minimum value is {rule.min_value}")

        if rule.max_value is not None:
            if isinstance(validated_value, (int, float)):
                if validated_value > rule.max_value:
                    raise InputValidationError(field, f"Maximum value is {rule.max_value}")

        # Pattern validation
        if rule.pattern:
            if isinstance(validated_value, str):
                if not re.match(rule.pattern, validated_value):
                    raise InputValidationError(field, f"Value does not match pattern: {rule.pattern}")

        # Allowed values validation
        if rule.allowed_values:
            if validated_value not in rule.allowed_values:
                raise InputValidationError(field, f"Value must be one of: {rule.allowed_values}")

        # Schema validation
        if rule.schema:
            if rule.validation_type == ValidationType.JSON:
                self._validate_json_schema(validated_value, rule.schema)
            elif rule.validation_type == ValidationType.DICT:
                self._validate_dict_schema(validated_value, rule.schema)

        # Custom validation
        if rule.custom_validator:
            try:
                validated_value = rule.custom_validator(validated_value)
            except Exception as e:
                raise InputValidationError(field, f"Custom validation failed: {e}")

        # Sanitize if requested
        if rule.sanitize:
            validated_value = self._sanitize_value(validated_value, rule)

        return validated_value

    def _validate_type(self, value: Any, rule: ValidationRule) -> Any:
        """Validate value type.

        Args:
            value: Value to validate
            rule: Validation rule

        Returns:
            Value converted to correct type

        Raises:
            InputValidationError: If type conversion fails
        """
        try:
            if rule.validation_type == ValidationType.STRING:
                return str(value)
            elif rule.validation_type == ValidationType.INTEGER:
                return int(value)
            elif rule.validation_type == ValidationType.FLOAT:
                return float(value)
            elif rule.validation_type == ValidationType.BOOLEAN:
                if isinstance(value, str):
                    return value.lower() in ('true', '1', 'yes', 'on')
                return bool(value)
            elif rule.validation_type == ValidationType.LIST:
                if isinstance(value, str):
                    # Try to parse as JSON
                    return json.loads(value)
                elif not isinstance(value, list):
                    return [value]
                return value
            elif rule.validation_type == ValidationType.DICT:
                if isinstance(value, str):
                    # Try to parse as JSON
                    parsed = json.loads(value)
                    if not isinstance(parsed, dict):
                        raise ValueError("Not a dictionary")
                    return parsed
                elif not isinstance(value, dict):
                    raise ValueError("Not a dictionary")
                return value
            elif rule.validation_type == ValidationType.DATETIME:
                if isinstance(value, str):
                    # Try ISO format first
                    try:
                        return datetime.fromisoformat(value)
                    except Exception:
                        # Try timestamp
                        return datetime.fromtimestamp(float(value))
                elif isinstance(value, (int, float)):
                    return datetime.fromtimestamp(value)
                return value
            elif rule.validation_type == ValidationType.JSON:
                if isinstance(value, str):
                    parsed = json.loads(value)
                else:
                    parsed = value
                # Validate it's valid JSON
                json.dumps(parsed)
                return parsed
            elif rule.validation_type == ValidationType.XML:
                if isinstance(value, str):
                    # Parse XML to ensure it's valid
                    root = ET.fromstring(value)
                    return value
                raise ValueError("XML must be a string")
            else:
                return value

        except (ValueError, TypeError, json.JSONDecodeError, ET.ParseError) as e:
            raise InputValidationError("type", f"Invalid type conversion: {e}")

    def _validate_json_schema(self, value: Any, schema: dict[str, Any]) -> None:
        """Validate JSON against schema.

        Args:
            value: JSON value
            schema: JSON schema

        Raises:
            InputValidationError: If validation fails
        """
        # Simplified schema validation
        # In practice, use jsonschema library for full validation
        if "type" in schema:
            expected_type = schema["type"]
            if expected_type == "object" and not isinstance(value, dict):
                raise InputValidationError("json", f"Expected object, got {type(value)}")
            elif expected_type == "array" and not isinstance(value, list):
                raise InputValidationError("json", f"Expected array, got {type(value)}")
            elif expected_type == "string" and not isinstance(value, str):
                raise InputValidationError("json", f"Expected string, got {type(value)}")

        if "properties" in schema and isinstance(value, dict):
            for prop, prop_schema in schema["properties"].items():
                if prop in value:
                    # Recursively validate
                    validator = InputValidator(f"{self.name}_{prop}")
                    rule = ValidationRule(
                        prop,
                        self._get_validation_type_from_schema(prop_schema),
                        required=schema.get("required", {}).get(prop, False)
                    )
                    validator.add_rule(prop, rule)
                    validator.validate({prop: value[prop]}, strict=False)

    def _validate_dict_schema(self, value: dict[str, Any], schema: dict[str, Any]) -> None:
        """Validate dictionary against schema.

        Args:
            value: Dictionary value
            schema: Schema definition

        Raises:
            InputValidationError: If validation fails
        """
        for key, key_schema in schema.items():
            if key in value:
                # Check type
                expected_type = key_schema.get("type")
                if expected_type and not isinstance(value[key], expected_type):
                    raise InputValidationError(key, f"Expected {expected_type.__name__}")

    def _get_validation_type_from_schema(self, schema: dict[str, Any]) -> ValidationType:
        """Get validation type from schema.

        Args:
            schema: Schema definition

        Returns:
            Validation type
        """
        type_map = {
            "string": ValidationType.STRING,
            "integer": ValidationType.INTEGER,
            "number": ValidationType.FLOAT,
            "boolean": ValidationType.BOOLEAN,
            "array": ValidationType.LIST,
            "object": ValidationType.DICT
        }
        return type_map.get(schema.get("type", "string"), ValidationType.STRING)

    def _sanitize_value(self, value: Any, rule: ValidationRule) -> Any:
        """Sanitize a value.

        Args:
            value: Value to sanitize
            rule: Validation rule

        Returns:
            Sanitized value
        """
        if isinstance(value, str):
            # Remove control characters
            value = ''.join(char for char in value if ord(char) >= 32 or char in '\n\r\t')

            # Limit length
            if rule.max_length:
                value = value[:rule.max_length]

            # Normalize whitespace
            value = ' '.join(value.split())

        elif isinstance(value, list):
            # Remove None values
            value = [v for v in value if v is not None]

            # Limit length
            if rule.max_length:
                value = value[:rule.max_length]

        return value


# Predefined validation rules
COMMON_RULES = {
    "hop_id": ValidationRule(
        "hop_id",
        ValidationType.STRING,
        required=True,
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_-]+$"
    ),
    "context_data": ValidationRule(
        "context_data",
        ValidationType.DICT,
        required=False,
        max_length=1000  # Max 1000 keys
    ),
    "retry_count": ValidationRule(
        "retry_count",
        ValidationType.INTEGER,
        required=False,
        min_value=0,
        max_value=10
    ),
    "timeout": ValidationRule(
        "timeout",
        ValidationType.FLOAT,
        required=False,
        min_value=0.1,
        max_value=300.0
    ),
    "json_payload": ValidationRule(
        "json_payload",
        ValidationType.JSON,
        required=False,
        max_length=10000  # Max 10KB
    ),
    "xml_content": ValidationRule(
        "xml_content",
        ValidationType.XML,
        required=False,
        max_length=50000  # Max 50KB
    )
}


def create_default_validator() -> InputValidator:
    """Create a validator with common rules.

    Returns:
        InputValidator with predefined rules
    """
    validator = InputValidator("default")

    for name, rule in COMMON_RULES.items():
        validator.add_rule(name, rule)

    return validator


# Pydantic model for automatic validation
class ValidatedInput(BaseModel):
    """Base model for validated input."""

    class Config:
        # Validate assignment
        validate_assignment = True
        # Use enum values
        use_enum_values = True
        # Extra fields forbidden
        extra = "forbid"

    @validator('*')
    def sanitize_strings(cls, v):
        """Sanitize string fields."""
        if isinstance(v, str):
            # Remove control characters
            v = ''.join(char for char in v if ord(char) >= 32 or char in '\n\r\t')
            # Strip whitespace
            v = v.strip()
        return v

    @validator('*')
    def check_size(cls, v):
        """Check size limits."""
        if isinstance(v, str) and len(v) > 10000:
            raise ValueError("String too long")
        if isinstance(v, (list, dict)) and len(v) > 1000:
            raise ValueError("Collection too large")
        return v


def validate_with_pydantic(data: dict[str, Any], model_class: type[ValidatedInput]) -> ValidatedInput:
    """Validate data using Pydantic model.

    Args:
        data: Data to validate
        model_class: Pydantic model class

    Returns:
        Validated model instance

    Raises:
        ValidationError: If validation fails
    """
    try:
        return model_class(**data)
    except ValidationError as e:
        # Convert to InputValidationError for consistency
        errors = []
        for error in e.errors():
            field = '.'.join(str(x) for x in error['loc'])
            errors.append(f"{field}: {error['msg']}")
        raise InputValidationError("pydantic", f"Validation failed: {', '.join(errors)}")
