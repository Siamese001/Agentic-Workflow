"""Validate Input Schema - Utility for validating input data against schemas.

This module provides utilities for validating input data against various schema
definitions, including JSON Schema, custom validation rules, and type checking.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Levels of validation strictness."""
    STRICT = "strict"
    MODERATE = "moderate"
    LENIENT = "lenient"


class ValidationType(Enum):
    """Types of validation to perform."""
    TYPE = "type"
    FORMAT = "format"
    RANGE = "range"
    PATTERN = "pattern"
    REQUIRED = "required"
    CUSTOM = "custom"


@dataclass
class ValidationError:
    """Individual validation error."""
    field_path: str
    error_type: ValidationType
    message: str
    expected: Optional[Any] = None
    actual: Optional[Any] = None


@dataclass
class ValidationResult:
    """Result of schema validation."""
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    validated_data: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FieldDefinition:
    """Definition of a field in the schema."""
    name: str
    type: str
    required: bool = False
    default_value: Any = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None
    enum_values: Optional[List[Any]] = None
    custom_validator: Optional[str] = None


@dataclass
class InputSchema:
    """Definition of an input schema."""
    name: str
    version: str
    fields: Dict[str, FieldDefinition]
    allow_extra_fields: bool = False
    strict_mode: bool = False


@dataclass
class ValidationConfig:
    """Configuration for validation operations."""
    level: ValidationLevel = ValidationLevel.MODERATE
    stop_on_first_error: bool = False
    coerce_types: bool = False
    remove_extra_fields: bool = False


class InputSchemaValidator:
    """Main class for validating input schemas."""

    def __init__(self, config: Optional[ValidationConfig] = None):
        self.config = config or ValidationConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._custom_validators = self._initialize_custom_validators()

    def validate(self, data: Dict[str, Any], schema: InputSchema) -> ValidationResult:
        """Validate input data against schema.
        
        Args:
            data: Input data to validate
            schema: Schema definition
            
        Returns:
            ValidationResult: Validation result with errors and warnings
        """
        self.logger.info(f"Validating data against schema: {schema.name}")
        
        try:
            errors = []
            warnings = []
            validated_data = data.copy()
            
            # Check required fields
            missing_fields = self._check_required_fields(data, schema)
            errors.extend(missing_fields)
            
            # Validate each field
            for field_name, field_def in schema.fields.items():
                if field_name in data:
                    field_errors = self._validate_field(
                        data[field_name], 
                        field_def, 
                        field_name
                    )
                    errors.extend(field_errors)
            
            # Check for extra fields
            if not schema.allow_extra_fields:
                extra_fields = self._check_extra_fields(data, schema)
                if self.config.level == ValidationLevel.STRICT:
                    errors.extend(extra_fields)
                else:
                    warnings.extend([f"Extra field found: {e.field_path}" for e in extra_fields])
                    if self.config.remove_extra_fields:
                        for extra in extra_fields:
                            validated_data.pop(extra.field_path, None)
            
            # Apply default values for missing optional fields
            if self.config.level != ValidationLevel.STRICT:
                for field_name, field_def in schema.fields.items():
                    if field_name not in validated_data and field_def.default_value is not None:
                        validated_data[field_name] = field_def.default_value
                        warnings.append(f"Applied default value for field: {field_name}")
            
            # Type coercion if enabled
            if self.config.coerce_types:
                validated_data = self._coerce_types(validated_data, schema)
            
            result = ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                validated_data=validated_data,
                metadata={
                    "validated_at": datetime.utcnow().isoformat(),
                    "schema_name": schema.name,
                    "schema_version": schema.version,
                    "validation_level": self.config.level.value
                }
            )
            
            self.logger.info(f"Validation completed: {'PASS' if result.is_valid else 'FAIL'}")
            return result
            
        except Exception as e:
            self.logger.error(f"Validation failed: {str(e)}")
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError(
                    field_path="root",
                    error_type=ValidationType.CUSTOM,
                    message=f"Validation error: {str(e)}"
                )],
                metadata={"error": str(e)}
            )

    def validate_batch(self, data_list: List[Dict[str, Any]], 
                      schema: InputSchema) -> List[ValidationResult]:
        """Validate multiple data items against schema.
        
        Args:
            data_list: List of data items to validate
            schema: Schema definition
            
        Returns:
            List[ValidationResult]: Results for each item
        """
        results = []
        
        for i, data in enumerate(data_list):
            self.logger.debug(f"Validating item {i+1}/{len(data_list)}")
            result = self.validate(data, schema)
            results.append(result)
            
            if self.config.stop_on_first_error and not result.is_valid:
                break
        
        return results

    def add_custom_validator(self, name: str, validator_func: Callable[[Any], bool]) -> None:
        """Add a custom validation function.
        
        Args:
            name: Name of the validator
            validator_func: Validation function that returns True if valid
        """
        self._custom_validators[name] = validator_func
        self.logger.info(f"Added custom validator: {name}")

    def _check_required_fields(self, data: Dict[str, Any], schema: InputSchema) -> List[ValidationError]:
        """Check for missing required fields."""
        errors = []
        
        for field_name, field_def in schema.fields.items():
            if field_def.required and field_name not in data:
                errors.append(ValidationError(
                    field_path=field_name,
                    error_type=ValidationType.REQUIRED,
                    message=f"Required field is missing",
                    expected=field_name,
                    actual=None
                ))
        
        return errors

    def _check_extra_fields(self, data: Dict[str, Any], schema: InputSchema) -> List[ValidationError]:
        """Check for unexpected extra fields."""
        errors = []
        
        for field_name in data:
            if field_name not in schema.fields:
                errors.append(ValidationError(
                    field_path=field_name,
                    error_type=ValidationType.CUSTOM,
                    message=f"Unexpected field found",
                    expected=None,
                    actual=field_name
                ))
        
        return errors

    def _validate_field(self, value: Any, field_def: FieldDefinition, field_path: str) -> List[ValidationError]:
        """Validate a single field value."""
        errors = []
        
        # Type validation
        type_error = self._validate_type(value, field_def.type, field_path)
        if type_error:
            errors.append(type_error)
        
        # Range validation
        if field_def.min_value is not None or field_def.max_value is not None:
            range_error = self._validate_range(value, field_def, field_path)
            if range_error:
                errors.append(range_error)
        
        # Pattern validation
        if field_def.pattern:
            pattern_error = self._validate_pattern(value, field_def.pattern, field_path)
            if pattern_error:
                errors.append(pattern_error)
        
        # Enum validation
        if field_def.enum_values:
            enum_error = self._validate_enum(value, field_def.enum_values, field_path)
            if enum_error:
                errors.append(enum_error)
        
        # Custom validation
        if field_def.custom_validator:
            custom_error = self._validate_custom(value, field_def.custom_validator, field_path)
            if custom_error:
                errors.append(custom_error)
        
        return errors

    def _validate_type(self, value: Any, expected_type: str, field_path: str) -> Optional[ValidationError]:
        """Validate field type."""
        type_map = {
            "string": str,
            "integer": int,
            "float": float,
            "boolean": bool,
            "array": list,
            "object": dict,
            "null": type(None)
        }
        
        expected_python_type = type_map.get(expected_type)
        if not expected_python_type:
            return ValidationError(
                field_path=field_path,
                error_type=ValidationType.TYPE,
                message=f"Unknown type: {expected_type}"
            )
        
        if not isinstance(value, expected_python_type):
            # Allow int for float in lenient mode
            if self.config.level == ValidationLevel.LENIENT and expected_type == "float" and isinstance(value, int):
                return None
            
            return ValidationError(
                field_path=field_path,
                error_type=ValidationType.TYPE,
                message=f"Type mismatch",
                expected=expected_type,
                actual=type(value).__name__
            )
        
        return None

    def _validate_range(self, value: Any, field_def: FieldDefinition, field_path: str) -> Optional[ValidationError]:
        """Validate numeric range."""
        if not isinstance(value, (int, float)):
            return None
        
        if field_def.min_value is not None and value < field_def.min_value:
            return ValidationError(
                field_path=field_path,
                error_type=ValidationType.RANGE,
                message=f"Value below minimum",
                expected=f">= {field_def.min_value}",
                actual=value
            )
        
        if field_def.max_value is not None and value > field_def.max_value:
            return ValidationError(
                field_path=field_path,
                error_type=ValidationType.RANGE,
                message=f"Value above maximum",
                expected=f"<= {field_def.max_value}",
                actual=value
            )
        
        return None

    def _validate_pattern(self, value: Any, pattern: str, field_path: str) -> Optional[ValidationError]:
        """Validate string pattern."""
        if not isinstance(value, str):
            return None
        
        import re
        if not re.match(pattern, value):
            return ValidationError(
                field_path=field_path,
                error_type=ValidationType.PATTERN,
                message=f"String does not match pattern",
                expected=pattern,
                actual=value
            )
        
        return None

    def _validate_enum(self, value: Any, enum_values: List[Any], field_path: str) -> Optional[ValidationError]:
        """Validate enum values."""
        if value not in enum_values:
            return ValidationError(
                field_path=field_path,
                error_type=ValidationType.CUSTOM,
                message=f"Value not in allowed enum",
                expected=enum_values,
                actual=value
            )
        
        return None

    def _validate_custom(self, value: Any, validator_name: str, field_path: str) -> Optional[ValidationError]:
        """Validate using custom validator."""
        if validator_name not in self._custom_validators:
            return ValidationError(
                field_path=field_path,
                error_type=ValidationType.CUSTOM,
                message=f"Unknown custom validator: {validator_name}"
            )
        
        validator = self._custom_validators[validator_name]
        try:
            if not validator(value):
                return ValidationError(
                    field_path=field_path,
                    error_type=ValidationType.CUSTOM,
                    message=f"Custom validation failed",
                    expected="validator returns True",
                    actual="validator returned False"
                )
        except Exception as e:
            return ValidationError(
                field_path=field_path,
                error_type=ValidationType.CUSTOM,
                message=f"Custom validator error: {str(e)}"
            )
        
        return None

    def _coerce_types(self, data: Dict[str, Any], schema: InputSchema) -> Dict[str, Any]:
        """Coerce types to match schema."""
        coerced = data.copy()
        
        for field_name, field_def in schema.fields.items():
            if field_name in coerced:
                value = coerced[field_name]
                coerced_value = self._coerce_value(value, field_def.type)
                if coerced_value is not None:
                    coerced[field_name] = coerced_value
        
        return coerced

    def _coerce_value(self, value: Any, target_type: str) -> Any:
        """Coerce a single value to target type."""
        try:
            if target_type == "string":
                return str(value)
            elif target_type == "integer":
                return int(float(value))
            elif target_type == "float":
                return float(value)
            elif target_type == "boolean":
                if isinstance(value, str):
                    return value.lower() in ("true", "1", "yes", "on")
                return bool(value)
            else:
                return value
        except (ValueError, TypeError):
            return None

    def _initialize_custom_validators(self) -> Dict[str, Callable]:
        """Initialize built-in custom validators."""
        return {
            "email": lambda x: isinstance(x, str) and "@" in x and "." in x.split("@")[1],
            "url": lambda x: isinstance(x, str) and (x.startswith("http://") or x.startswith("https://")),
            "positive": lambda x: isinstance(x, (int, float)) and x > 0,
            "non_negative": lambda x: isinstance(x, (int, float)) and x >= 0,
            "non_empty_string": lambda x: isinstance(x, str) and len(x.strip()) > 0
        }


# Factory function for easy instantiation
def create_input_schema_validator(
    level: str = "moderate",
    stop_on_first_error: bool = False,
    coerce_types: bool = False,
    **kwargs
) -> InputSchemaValidator:
    """Create a configured input schema validator."""
    config = ValidationConfig(
        level=ValidationLevel(level),
        stop_on_first_error=stop_on_first_error,
        coerce_types=coerce_types,
        **kwargs
    )
    return InputSchemaValidator(config)


# Convenience function for direct usage
def validate_input_schema(
    data: Dict[str, Any],
    schema: Dict[str, Any],
    level: str = "moderate",
    strict_mode: bool = False
) -> Dict[str, Any]:
    """Validate input data against schema.
    
    Args:
        data: Input data to validate
        schema: Schema definition
        level: Validation level
        strict_mode: Whether to use strict validation
        
    Returns:
        Dict: Validation result
    """
    validator = create_input_schema_validator(level=level)
    
    # Convert schema
    fields = {}
    for name, field_def in schema.get("fields", {}).items():
        fields[name] = FieldDefinition(
            name=name,
            type=field_def.get("type", "string"),
            required=field_def.get("required", False),
            default_value=field_def.get("default"),
            min_value=field_def.get("min_value"),
            max_value=field_def.get("max_value"),
            pattern=field_def.get("pattern"),
            enum_values=field_def.get("enum"),
            custom_validator=field_def.get("custom_validator")
        )
    
    input_schema = InputSchema(
        name=schema.get("name", "unnamed"),
        version=schema.get("version", "1.0"),
        fields=fields,
        allow_extra_fields=schema.get("allow_extra_fields", False),
        strict_mode=strict_mode
    )
    
    # Validate
    result = validator.validate(data, input_schema)
    
    return {
        "is_valid": result.is_valid,
        "errors": [
            {
                "field_path": e.field_path,
                "error_type": e.error_type.value,
                "message": e.message,
                "expected": e.expected,
                "actual": e.actual
            }
            for e in result.errors
        ],
        "warnings": result.warnings,
        "validated_data": result.validated_data,
        "metadata": result.metadata
    }
