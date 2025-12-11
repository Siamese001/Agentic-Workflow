"""Safety-Enhanced RAG Schema Validation - Validates RAG schemas with safety constraints.

This module provides schema validation for RAG operations with additional safety checks,
ensuring data integrity, type safety, and security compliance.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Type
import logging
import json
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class SchemaType(Enum):
    """Types of RAG schemas."""
    QUERY_SCHEMA = "query_schema"
    DOCUMENT_SCHEMA = "document_schema"
    RESPONSE_SCHEMA = "response_schema"
    METADATA_SCHEMA = "metadata_schema"
    RETRIEVAL_SCHEMA = "retrieval_schema"
    GENERATION_SCHEMA = "generation_schema"


class ValidationLevel(Enum):
    """Levels of schema validation."""
    BASIC = "basic"
    STRICT = "strict"
    SECURITY = "security"
    COMPREHENSIVE = "comprehensive"


class ValidationErrorType(Enum):
    """Types of validation errors."""
    TYPE_MISMATCH = "type_mismatch"
    MISSING_FIELD = "missing_field"
    INVALID_VALUE = "invalid_value"
    SECURITY_VIOLATION = "security_violation"
    CONSTRAINT_VIOLATION = "constraint_violation"
    SCHEMA_MISMATCH = "schema_mismatch"


@dataclass
class SchemaField:
    """Definition of a schema field."""
    name: str
    field_type: str
    required: bool = True
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    allowed_values: Optional[List[str]] = None
    pattern: Optional[str] = None
    safety_check: Optional[str] = None
    description: str = ""


@dataclass
class SchemaDefinition:
    """Definition of a RAG schema."""
    schema_type: SchemaType
    version: str
    fields: List[SchemaField]
    validation_level: ValidationLevel = ValidationLevel.BASIC
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationError:
    """Record of a schema validation error."""
    error_type: ValidationErrorType
    field_name: str
    message: str
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None
    severity: str = "error"


@dataclass
class ValidationResult:
    """Result of schema validation."""
    valid: bool
    schema_type: SchemaType
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    sanitized_data: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SafetyRAGSchemaConfig:
    """Configuration for safety RAG schema validation."""
    enable_type_validation: bool = True
    enable_length_validation: bool = True
    enable_pattern_validation: bool = True
    enable_safety_validation: bool = True
    sanitize_invalid_data: bool = True
    strict_mode: bool = False
    custom_validators: Dict[str, callable] = field(default_factory=dict)
    log_level: str = "INFO"


class SafetyRAGSchemaValidator:
    """Main class for safety-enhanced RAG schema validation."""

    def __init__(self, config: Optional[SafetyRAGSchemaConfig] = None):
        self.config = config or SafetyRAGSchemaConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)
        self._schemas = {}
        self._load_default_schemas()

    def validate(self, data: Dict[str, Any], schema_type: SchemaType) -> ValidationResult:
        """Validate data against a RAG schema with safety checks.
        
        Args:
            data: Data to validate
            schema_type: Type of schema to validate against
            
        Returns:
            ValidationResult: Result of validation with errors and warnings
        """
        self.logger.info(f"Validating data against {schema_type.value} schema")
        
        errors = []
        warnings = []
        sanitized_data = data.copy() if self.config.sanitize_invalid_data else None
        
        try:
            # Get schema definition
            schema = self._get_schema(schema_type)
            if not schema:
                errors.append(ValidationError(
                    error_type=ValidationErrorType.SCHEMA_MISMATCH,
                    field_name="schema",
                    message=f"Schema not found: {schema_type.value}"
                ))
                return ValidationResult(
                    valid=False,
                    schema_type=schema_type,
                    errors=errors
                )
            
            # Validate each field
            for field in schema.fields:
                field_errors = self._validate_field(field, data, sanitized_data)
                errors.extend(field_errors)
            
            # Run custom validators
            for validator_name, validator_func in self.config.custom_validators.items():
                try:
                    custom_errors = validator_func(data, schema)
                    if custom_errors:
                        errors.extend(custom_errors)
                except Exception as e:
                    self.logger.warning(f"Custom validator {validator_name} failed: {str(e)}")
            
            # Determine validity
            valid = len(errors) == 0
            
            result = ValidationResult(
                valid=valid,
                schema_type=schema_type,
                errors=errors,
                warnings=warnings,
                sanitized_data=sanitized_data,
                metadata={
                    "validated_at": datetime.utcnow().isoformat(),
                    "schema_version": schema.version,
                    "validation_level": schema.validation_level.value,
                    "validator": "SafetyRAGSchemaValidator"
                }
            )
            
            self.logger.info(
                f"Schema validation completed: {'valid' if valid else 'invalid'} "
                f"({len(errors)} errors, {len(warnings)} warnings)"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Schema validation failed: {str(e)}")
            return ValidationResult(
                valid=False,
                schema_type=schema_type,
                errors=[ValidationError(
                    error_type=ValidationErrorType.SCHEMA_MISMATCH,
                    field_name="system",
                    message=f"Validation failed: {str(e)}"
                )],
                metadata={"error": str(e)}
            )

    def _validate_field(self, field: SchemaField, data: Dict[str, Any], sanitized_data: Optional[Dict[str, Any]]) -> List[ValidationError]:
        """Validate a single field."""
        errors = []
        value = data.get(field.name)
        
        # Check required field
        if field.required and value is None:
            errors.append(ValidationError(
                error_type=ValidationErrorType.MISSING_FIELD,
                field_name=field.name,
                message=f"Required field missing: {field.name}"
            ))
            return errors
        
        # Skip validation if field is not provided and not required
        if value is None:
            return errors
        
        # Type validation
        if self.config.enable_type_validation:
            type_error = self._validate_type(field, value)
            if type_error:
                errors.append(type_error)
        
        # Length validation
        if self.config.enable_length_validation and isinstance(value, str):
            length_errors = self._validate_length(field, value)
            errors.extend(length_errors)
        
        # Pattern validation
        if self.config.enable_pattern_validation and field.pattern and isinstance(value, str):
            pattern_error = self._validate_pattern(field, value)
            if pattern_error:
                errors.append(pattern_error)
        
        # Allowed values validation
        if field.allowed_values and isinstance(value, str):
            if value not in field.allowed_values:
                errors.append(ValidationError(
                    error_type=ValidationErrorType.INVALID_VALUE,
                    field_name=field.name,
                    message=f"Value '{value}' not in allowed values: {field.allowed_values}",
                    actual_value=str(value)
                ))
        
        # Safety validation
        if self.config.enable_safety_validation and field.safety_check:
            safety_errors = self._validate_safety(field, value, sanitized_data)
            errors.extend(safety_errors)
        
        return errors

    def _validate_type(self, field: SchemaField, value: Any) -> Optional[ValidationError]:
        """Validate field type."""
        expected_type = field.field_type.lower()
        
        if expected_type == "string" and not isinstance(value, str):
            return ValidationError(
                error_type=ValidationErrorType.TYPE_MISMATCH,
                field_name=field.name,
                message=f"Expected string, got {type(value).__name__}",
                expected_value="string",
                actual_value=type(value).__name__
            )
        elif expected_type == "integer" and not isinstance(value, int):
            return ValidationError(
                error_type=ValidationErrorType.TYPE_MISMATCH,
                field_name=field.name,
                message=f"Expected integer, got {type(value).__name__}",
                expected_value="integer",
                actual_value=type(value).__name__
            )
        elif expected_type == "float" and not isinstance(value, (int, float)):
            return ValidationError(
                error_type=ValidationErrorType.TYPE_MISMATCH,
                field_name=field.name,
                message=f"Expected number, got {type(value).__name__}",
                expected_value="number",
                actual_value=type(value).__name__
            )
        elif expected_type == "boolean" and not isinstance(value, bool):
            return ValidationError(
                error_type=ValidationErrorType.TYPE_MISMATCH,
                field_name=field.name,
                message=f"Expected boolean, got {type(value).__name__}",
                expected_value="boolean",
                actual_value=type(value).__name__
            )
        elif expected_type == "array" and not isinstance(value, list):
            return ValidationError(
                error_type=ValidationErrorType.TYPE_MISMATCH,
                field_name=field.name,
                message=f"Expected array, got {type(value).__name__}",
                expected_value="array",
                actual_value=type(value).__name__
            )
        elif expected_type == "object" and not isinstance(value, dict):
            return ValidationError(
                error_type=ValidationErrorType.TYPE_MISMATCH,
                field_name=field.name,
                message=f"Expected object, got {type(value).__name__}",
                expected_value="object",
                actual_value=type(value).__name__
            )
        
        return None

    def _validate_length(self, field: SchemaField, value: str) -> List[ValidationError]:
        """Validate field length."""
        errors = []
        length = len(value)
        
        if field.min_length is not None and length < field.min_length:
            errors.append(ValidationError(
                error_type=ValidationErrorType.CONSTRAINT_VIOLATION,
                field_name=field.name,
                message=f"Value too short: {length} < {field.min_length}",
                actual_value=str(length)
            ))
        
        if field.max_length is not None and length > field.max_length:
            errors.append(ValidationError(
                error_type=ValidationErrorType.CONSTRAINT_VIOLATION,
                field_name=field.name,
                message=f"Value too long: {length} > {field.max_length}",
                actual_value=str(length)
            ))
        
        return errors

    def _validate_pattern(self, field: SchemaField, value: str) -> Optional[ValidationError]:
        """Validate field pattern."""
        import re
        if not re.match(field.pattern, value):
            return ValidationError(
                error_type=ValidationErrorType.INVALID_VALUE,
                field_name=field.name,
                message=f"Value does not match pattern: {field.pattern}",
                actual_value=value
            )
        return None

    def _validate_safety(self, field: SchemaField, value: str, sanitized_data: Optional[Dict[str, Any]]) -> List[ValidationError]:
        """Validate field safety."""
        errors = []
        
        # Check for potential security issues
        if field.safety_check == "no_html":
            if "<" in value and ">" in value:
                errors.append(ValidationError(
                    error_type=ValidationErrorType.SECURITY_VIOLATION,
                    field_name=field.name,
                    message="HTML tags not allowed",
                    actual_value=value[:50] + "..." if len(value) > 50 else value
                ))
                # Sanitize if enabled
                if sanitized_data and field.name in sanitized_data:
                    sanitized_data[field.name] = value.replace("<", "&lt;").replace(">", "&gt;")
        
        elif field.safety_check == "no_sql":
            sql_keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "UNION"]
            if any(keyword in value.upper() for keyword in sql_keywords):
                errors.append(ValidationError(
                    error_type=ValidationErrorType.SECURITY_VIOLATION,
                    field_name=field.name,
                    message="Potential SQL injection detected",
                    actual_value=value[:50] + "..." if len(value) > 50 else value
                ))
        
        elif field.safety_check == "no_script":
            if "javascript:" in value.lower() or "<script" in value.lower():
                errors.append(ValidationError(
                    error_type=ValidationErrorType.SECURITY_VIOLATION,
                    field_name=field.name,
                    message="Script content not allowed",
                    actual_value=value[:50] + "..." if len(value) > 50 else value
                ))
        
        return errors

    def _load_default_schemas(self) -> None:
        """Load default RAG schemas."""
        # Query schema
        self._schemas[SchemaType.QUERY_SCHEMA] = SchemaDefinition(
            schema_type=SchemaType.QUERY_SCHEMA,
            version="1.0",
            validation_level=ValidationLevel.STRICT,
            fields=[
                SchemaField(
                    name="query",
                    field_type="string",
                    required=True,
                    min_length=1,
                    max_length=1000,
                    safety_check="no_script",
                    description="Search query text"
                ),
                SchemaField(
                    name="top_k",
                    field_type="integer",
                    required=False,
                    min_value=1,
                    max_value=100,
                    description="Number of results to return"
                ),
                SchemaField(
                    name="filters",
                    field_type="object",
                    required=False,
                    description="Query filters"
                )
            ]
        )
        
        # Document schema
        self._schemas[SchemaType.DOCUMENT_SCHEMA] = SchemaDefinition(
            schema_type=SchemaType.DOCUMENT_SCHEMA,
            version="1.0",
            validation_level=ValidationLevel.BASIC,
            fields=[
                SchemaField(
                    name="id",
                    field_type="string",
                    required=True,
                    pattern=r"^[a-zA-Z0-9_-]+$",
                    description="Document identifier"
                ),
                SchemaField(
                    name="content",
                    field_type="string",
                    required=True,
                    min_length=1,
                    max_length=10000,
                    safety_check="no_script",
                    description="Document content"
                ),
                SchemaField(
                    name="metadata",
                    field_type="object",
                    required=False,
                    description="Document metadata"
                )
            ]
        )
        
        # Response schema
        self._schemas[SchemaType.RESPONSE_SCHEMA] = SchemaDefinition(
            schema_type=SchemaType.RESPONSE_SCHEMA,
            version="1.0",
            validation_level=ValidationLevel.SECURITY,
            fields=[
                SchemaField(
                    name="response",
                    field_type="string",
                    required=True,
                    min_length=1,
                    max_length=2000,
                    safety_check="no_script",
                    description="Generated response text"
                ),
                SchemaField(
                    name="confidence",
                    field_type="float",
                    required=False,
                    min_value=0.0,
                    max_value=1.0,
                    description="Response confidence score"
                ),
                SchemaField(
                    name="sources",
                    field_type="array",
                    required=False,
                    description="Source document IDs"
                )
            ]
        )

    def _get_schema(self, schema_type: SchemaType) -> Optional[SchemaDefinition]:
        """Get schema definition by type."""
        return self._schemas.get(schema_type)

    def add_schema(self, schema: SchemaDefinition) -> None:
        """Add a custom schema definition.
        
        Args:
            schema: Schema definition to add
        """
        self.logger.info(f"Adding schema: {schema.schema_type.value}")
        self._schemas[schema.schema_type] = schema

    def add_custom_validator(self, name: str, validator_func: callable) -> None:
        """Add a custom validator function.
        
        Args:
            name: Validator name
            validator_func: Validation function
        """
        self.logger.info(f"Adding custom validator: {name}")
        self.config.custom_validators[name] = validator_func


# Factory function for easy instantiation
def create_safety_rag_schema_validator(
    enable_type_validation: bool = True,
    enable_safety_validation: bool = True,
    strict_mode: bool = False,
    **kwargs
) -> SafetyRAGSchemaValidator:
    """Create a configured safety RAG schema validator."""
    config = SafetyRAGSchemaConfig(
        enable_type_validation=enable_type_validation,
        enable_safety_validation=enable_safety_validation,
        strict_mode=strict_mode,
        **kwargs
    )
    return SafetyRAGSchemaValidator(config)


# Convenience function for direct usage
def validate_rag_schema(
    data: Dict[str, Any],
    schema_type: str,
    enable_safety_validation: bool = True,
    strict_mode: bool = False,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Validate RAG data against schema with safety checks.
    
    Args:
        data: Data to validate
        schema_type: Type of schema to validate against
        enable_safety_validation: Whether to enable safety validation
        strict_mode: Whether to use strict validation mode
        config: Optional validator configuration overrides
        
    Returns:
        Dict: Validation result with errors and warnings
    """
    # Create validator and execute
    validator_config = SafetyRAGSchemaConfig(
        enable_safety_validation=enable_safety_validation,
        strict_mode=strict_mode,
        **config or {}
    )
    validator = SafetyRAGSchemaValidator(validator_config)
    result = validator.validate(data, SchemaType(schema_type))
    
    # Convert result to dict for JSON serialization
    return {
        "valid": result.valid,
        "schema_type": result.schema_type.value,
        "errors": [
            {
                "error_type": e.error_type.value,
                "field_name": e.field_name,
                "message": e.message,
                "expected_value": e.expected_value,
                "actual_value": e.actual_value,
                "severity": e.severity
            }
            for e in result.errors
        ],
        "warnings": result.warnings,
        "sanitized_data": result.sanitized_data,
        "metadata": result.metadata
    }
