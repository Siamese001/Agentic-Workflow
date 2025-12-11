"""RAG Schema Validation - Validates RAG operation schemas and data structures.

This module provides schema validation for RAG operations,
ensuring data integrity and type safety across the system.
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


class ValidationMode(Enum):
    """Schema validation modes."""
    STRICT = "strict"
    LENIENT = "lenient"
    PERMISSIVE = "permissive"


@dataclass
class FieldDefinition:
    """Definition of a schema field."""
    name: str
    field_type: str
    required: bool = True
    default_value: Any = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    allowed_values: Optional[List[Any]] = None
    description: str = ""


@dataclass
class RAGSchema:
    """RAG operation schema definition."""
    schema_id: str
    schema_type: SchemaType
    version: str
    fields: List[FieldDefinition]
    validation_mode: ValidationMode = ValidationMode.STRICT
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SchemaError:
    """Schema validation error."""
    field: str
    error_code: str
    message: str
    expected: Optional[str] = None
    actual: Optional[str] = None


@dataclass
class SchemaValidationResult:
    """Result of schema validation."""
    valid: bool
    schema_id: str
    errors: List[SchemaError] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    normalized_data: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RAGSchemaValidatorConfig:
    """Configuration for RAG schema validator."""
    auto_normalize: bool = True
    strict_type_checking: bool = True
    allow_extra_fields: bool = False
    fill_missing_defaults: bool = True
    log_validation_failures: bool = True
    custom_validators: Dict[str, callable] = field(default_factory=dict)
    log_level: str = "INFO"


class RAGSchemaValidator:
    """Main class for RAG schema validation."""

    def __init__(self, config: Optional[RAGSchemaValidatorConfig] = None):
        self.config = config or RAGSchemaValidatorConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)
        self._schemas = {}
        self._load_default_schemas()

    def validate(self, data: Dict[str, Any], schema_type: SchemaType) -> SchemaValidationResult:
        """Validate data against a RAG schema.
        
        Args:
            data: Data to validate
            schema_type: Type of schema to validate against
            
        Returns:
            SchemaValidationResult: Result of validation
        """
        self.logger.info(f"Validating data against {schema_type.value} schema")
        
        errors = []
        warnings = []
        normalized_data = data.copy() if self.config.auto_normalize else None
        
        try:
            # Get schema
            schema = self._get_schema(schema_type)
            if not schema:
                errors.append(SchemaError(
                    field="schema",
                    error_code="SCHEMA_NOT_FOUND",
                    message=f"Schema not found: {schema_type.value}"
                ))
                return SchemaValidationResult(
                    valid=False,
                    schema_id="unknown",
                    errors=errors
                )
            
            # Validate each field
            for field_def in schema.fields:
                field_errors = self._validate_field(field_def, data, normalized_data)
                errors.extend(field_errors)
            
            # Check for extra fields
            if not self.config.allow_extra_fields:
                defined_fields = {f.name for f in schema.fields}
                extra_fields = set(data.keys()) - defined_fields
                for extra_field in extra_fields:
                    warnings.append(f"Extra field not in schema: {extra_field}")
            
            # Run custom validators
            for validator_name, validator in self.config.custom_validators.items():
                try:
                    custom_errors = validator(data, schema)
                    if custom_errors:
                        errors.extend(custom_errors)
                except Exception as e:
                    self.logger.warning(f"Custom validator {validator_name} failed: {str(e)}")
            
            # Determine validity
            valid = len(errors) == 0
            
            result = SchemaValidationResult(
                valid=valid,
                schema_id=schema.schema_id,
                errors=errors,
                warnings=warnings,
                normalized_data=normalized_data,
                metadata={
                    "validated_at": datetime.utcnow().isoformat(),
                    "schema_version": schema.version,
                    "validation_mode": schema.validation_mode.value
                }
            )
            
            # Log validation failures
            if not valid and self.config.log_validation_failures:
                self._log_validation_errors(data, schema, errors)
            
            self.logger.info(
                f"Schema validation completed: {'valid' if valid else 'invalid'} "
                f"({len(errors)} errors, {len(warnings)} warnings)"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Schema validation failed: {str(e)}")
            return SchemaValidationResult(
                valid=False,
                schema_id="error",
                errors=[SchemaError(
                    field="system",
                    error_code="VALIDATION_ERROR",
                    message=f"Validation failed: {str(e)}"
                )]
            )

    def _validate_field(self, field_def: FieldDefinition, data: Dict[str, Any], normalized_data: Optional[Dict[str, Any]]) -> List[SchemaError]:
        """Validate a single field."""
        errors = []
        value = data.get(field_def.name)
        
        # Check required field
        if field_def.required and value is None:
            if field_def.default_value is not None:
                # Use default value
                if normalized_data is not None:
                    normalized_data[field_def.name] = field_def.default_value
            else:
                errors.append(SchemaError(
                    field=field_def.name,
                    error_code="REQUIRED_FIELD_MISSING",
                    message=f"Required field missing: {field_def.name}"
                ))
                return errors
        
        # Skip validation if field is not provided and not required
        if value is None:
            if field_def.default_value is not None and normalized_data is not None:
                normalized_data[field_def.name] = field_def.default_value
            return errors
        
        # Type validation
        type_error = self._validate_type(field_def, value)
        if type_error:
            errors.append(type_error)
            if self.config.validation_mode == ValidationMode.STRICT:
                return errors
        
        # Range validation for numbers
        if isinstance(value, (int, float)):
            range_errors = self._validate_range(field_def, value)
            errors.extend(range_errors)
        
        # Length validation for strings
        if isinstance(value, str):
            length_errors = self._validate_length(field_def, value)
            errors.extend(length_errors)
        
        # Allowed values validation
        if field_def.allowed_values is not None:
            if value not in field_def.allowed_values:
                errors.append(SchemaError(
                    field=field_def.name,
                    error_code="INVALID_VALUE",
                    message=f"Value '{value}' not in allowed values: {field_def.allowed_values}",
                    actual=str(value),
                    expected=str(field_def.allowed_values)
                ))
        
        return errors

    def _validate_type(self, field_def: FieldDefinition, value: Any) -> Optional[SchemaError]:
        """Validate field type."""
        expected_type = field_def.field_type.lower()
        
        if expected_type == "string" and not isinstance(value, str):
            return SchemaError(
                field=field_def.name,
                error_code="TYPE_MISMATCH",
                message=f"Expected string, got {type(value).__name__}",
                expected="string",
                actual=type(value).__name__
            )
        elif expected_type == "integer" and not isinstance(value, int):
            return SchemaError(
                field=field_def.name,
                error_code="TYPE_MISMATCH",
                message=f"Expected integer, got {type(value).__name__}",
                expected="integer",
                actual=type(value).__name__
            )
        elif expected_type == "float" and not isinstance(value, (int, float)):
            return SchemaError(
                field=field_def.name,
                error_code="TYPE_MISMATCH",
                message=f"Expected number, got {type(value).__name__}",
                expected="number",
                actual=type(value).__name__
            )
        elif expected_type == "boolean" and not isinstance(value, bool):
            return SchemaError(
                field=field_def.name,
                error_code="TYPE_MISMATCH",
                message=f"Expected boolean, got {type(value).__name__}",
                expected="boolean",
                actual=type(value).__name__
            )
        elif expected_type == "array" and not isinstance(value, list):
            return SchemaError(
                field=field_def.name,
                error_code="TYPE_MISMATCH",
                message=f"Expected array, got {type(value).__name__}",
                expected="array",
                actual=type(value).__name__
            )
        elif expected_type == "object" and not isinstance(value, dict):
            return SchemaError(
                field=field_def.name,
                error_code="TYPE_MISMATCH",
                message=f"Expected object, got {type(value).__name__}",
                expected="object",
                actual=type(value).__name__
            )
        
        return None

    def _validate_range(self, field_def: FieldDefinition, value: Union[int, float]) -> List[SchemaError]:
        """Validate numeric range."""
        errors = []
        
        if field_def.min_value is not None and value < field_def.min_value:
            errors.append(SchemaError(
                field=field_def.name,
                error_code="VALUE_TOO_SMALL",
                message=f"Value {value} is less than minimum {field_def.min_value}",
                actual=str(value),
                expected=f">= {field_def.min_value}"
            ))
        
        if field_def.max_value is not None and value > field_def.max_value:
            errors.append(SchemaError(
                field=field_def.name,
                error_code="VALUE_TOO_LARGE",
                message=f"Value {value} is greater than maximum {field_def.max_value}",
                actual=str(value),
                expected=f"<= {field_def.max_value}"
            ))
        
        return errors

    def _validate_length(self, field_def: FieldDefinition, value: str) -> List[SchemaError]:
        """Validate string length."""
        errors = []
        length = len(value)
        
        if field_def.min_length is not None and length < field_def.min_length:
            errors.append(SchemaError(
                field=field_def.name,
                error_code="STRING_TOO_SHORT",
                message=f"String length {length} is less than minimum {field_def.min_length}",
                actual=str(length),
                expected=f">= {field_def.min_length}"
            ))
        
        if field_def.max_length is not None and length > field_def.max_length:
            errors.append(SchemaError(
                field=field_def.name,
                error_code="STRING_TOO_LONG",
                message=f"String length {length} is greater than maximum {field_def.max_length}",
                actual=str(length),
                expected=f"<= {field_def.max_length}"
            ))
        
        return errors

    def _load_default_schemas(self) -> None:
        """Load default RAG schemas."""
        # Query schema
        self._schemas[SchemaType.QUERY_SCHEMA] = RAGSchema(
            schema_id="rag_query_v1",
            schema_type=SchemaType.QUERY_SCHEMA,
            version="1.0",
            fields=[
                FieldDefinition(
                    name="query",
                    field_type="string",
                    required=True,
                    min_length=1,
                    max_length=1000,
                    description="Search query text"
                ),
                FieldDefinition(
                    name="top_k",
                    field_type="integer",
                    required=False,
                    default_value=10,
                    min_value=1,
                    max_value=100,
                    description="Number of results to return"
                ),
                FieldDefinition(
                    name="filters",
                    field_type="object",
                    required=False,
                    description="Query filters"
                )
            ]
        )
        
        # Document schema
        self._schemas[SchemaType.DOCUMENT_SCHEMA] = RAGSchema(
            schema_id="rag_document_v1",
            schema_type=SchemaType.DOCUMENT_SCHEMA,
            version="1.0",
            fields=[
                FieldDefinition(
                    name="id",
                    field_type="string",
                    required=True,
                    description="Document identifier"
                ),
                FieldDefinition(
                    name="content",
                    field_type="string",
                    required=True,
                    min_length=1,
                    max_length=10000,
                    description="Document content"
                ),
                FieldDefinition(
                    name="metadata",
                    field_type="object",
                    required=False,
                    description="Document metadata"
                ),
                FieldDefinition(
                    name="score",
                    field_type="float",
                    required=False,
                    min_value=0.0,
                    max_value=1.0,
                    description="Relevance score"
                )
            ]
        )
        
        # Response schema
        self._schemas[SchemaType.RESPONSE_SCHEMA] = RAGSchema(
            schema_id="rag_response_v1",
            schema_type=SchemaType.RESPONSE_SCHEMA,
            version="1.0",
            fields=[
                FieldDefinition(
                    name="response",
                    field_type="string",
                    required=True,
                    min_length=1,
                    max_length=2000,
                    description="Generated response"
                ),
                FieldDefinition(
                    name="sources",
                    field_type="array",
                    required=False,
                    description="Source document IDs"
                ),
                FieldDefinition(
                    name="confidence",
                    field_type="float",
                    required=False,
                    min_value=0.0,
                    max_value=1.0,
                    description="Response confidence"
                )
            ]
        )

    def _get_schema(self, schema_type: SchemaType) -> Optional[RAGSchema]:
        """Get schema by type."""
        return self._schemas.get(schema_type)

    def _log_validation_errors(self, data: Dict[str, Any], schema: RAGSchema, errors: List[SchemaError]) -> None:
        """Log validation errors."""
        for error in errors:
            self.logger.warning(
                f"Schema validation error - Schema: {schema.schema_id}, "
                f"Field: {error.field}, Error: {error.message}"
            )

    def add_schema(self, schema: RAGSchema) -> None:
        """Add a custom schema.
        
        Args:
            schema: Schema to add
        """
        self.logger.info(f"Adding schema: {schema.schema_id}")
        self._schemas[schema.schema_type] = schema

    def get_schema(self, schema_type: SchemaType) -> Optional[RAGSchema]:
        """Get schema definition.
        
        Args:
            schema_type: Type of schema
            
        Returns:
            RAGSchema: Schema definition or None
        """
        return self._get_schema(schema_type)


# Factory function for easy instantiation
def create_rag_schema_validator(
    auto_normalize: bool = True,
    strict_type_checking: bool = True,
    allow_extra_fields: bool = False,
    **kwargs
) -> RAGSchemaValidator:
    """Create a configured RAG schema validator."""
    config = RAGSchemaValidatorConfig(
        auto_normalize=auto_normalize,
        strict_type_checking=strict_type_checking,
        allow_extra_fields=allow_extra_fields,
        **kwargs
    )
    return RAGSchemaValidator(config)


# Convenience function for direct usage
def validate_rag_schema(
    data: Dict[str, Any],
    schema_type: str,
    strict_mode: bool = True,
    auto_normalize: bool = True,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Validate RAG data against schema.
    
    Args:
        data: Data to validate
        schema_type: Type of schema to validate against
        strict_mode: Whether to use strict validation
        auto_normalize: Whether to normalize data
        config: Optional validator configuration
        
    Returns:
        Dict: Validation result
    """
    # Create validator and execute
    validator_config = RAGSchemaValidatorConfig(
        auto_normalize=auto_normalize,
        strict_type_checking=strict_mode,
        **config or {}
    )
    validator = RAGSchemaValidator(validator_config)
    result = validator.validate(data, SchemaType(schema_type))
    
    # Convert result to dict for JSON serialization
    return {
        "valid": result.valid,
        "schema_id": result.schema_id,
        "errors": [
            {
                "field": e.field,
                "error_code": e.error_code,
                "message": e.message,
                "expected": e.expected,
                "actual": e.actual
            }
            for e in result.errors
        ],
        "warnings": result.warnings,
        "normalized_data": result.normalized_data,
        "metadata": result.metadata
    }
