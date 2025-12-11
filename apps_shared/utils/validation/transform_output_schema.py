"""Transform Output Schema - Utility for transforming data between schemas.

This module provides utilities for transforming data from one schema to another,
including field mapping, type conversion, and validation.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class TransformationType(Enum):
    """Types of schema transformations."""
    FIELD_MAPPING = "field_mapping"
    TYPE_CONVERSION = "type_conversion"
    VALUE_TRANSFORMATION = "value_transformation"
    NESTING_FLATTENING = "nesting_flattening"
    VALIDATION_ENFORCEMENT = "validation_enforcement"


class DataType(Enum):
    """Data types for schema fields."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    DATE = "date"
    DATETIME = "datetime"


@dataclass
class FieldMapping:
    """Mapping from source field to target field."""
    source_path: str
    target_path: str
    transform_func: Optional[str] = None
    required: bool = False
    default_value: Any = None


@dataclass
class SchemaDefinition:
    """Definition of a schema."""
    name: str
    version: str
    fields: Dict[str, Dict[str, Any]]
    required_fields: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TransformationConfig:
    """Configuration for schema transformation."""
    strict_mode: bool = False
    ignore_missing_fields: bool = True
    validate_output: bool = True
    preserve_order: bool = False


@dataclass
class TransformationResult:
    """Result of schema transformation."""
    transformed_data: Dict[str, Any]
    source_data: Dict[str, Any]
    target_schema: SchemaDefinition
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SchemaTransformer:
    """Main class for transforming data between schemas."""

    def __init__(self, config: Optional[TransformationConfig] = None):
        self.config = config or TransformationConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._type_converters = self._initialize_type_converters()

    def transform_schema(self, data: Dict[str, Any], 
                        source_schema: SchemaDefinition,
                        target_schema: SchemaDefinition,
                        field_mappings: List[FieldMapping]) -> TransformationResult:
        """Transform data from source schema to target schema.
        
        Args:
            data: Source data to transform
            source_schema: Definition of source schema
            target_schema: Definition of target schema
            field_mappings: List of field mappings
            
        Returns:
            TransformationResult: Transformed data with metadata
        """
        self.logger.info(f"Transforming data from {source_schema.name} to {target_schema.name}")
        
        try:
            # Validate source data against source schema
            if self.config.validate_output:
                validation_errors = self._validate_data(data, source_schema)
                if validation_errors and self.config.strict_mode:
                    return TransformationResult(
                        transformed_data={},
                        source_data=data,
                        target_schema=target_schema,
                        errors=validation_errors,
                        metadata={"error": "Source data validation failed"}
                    )
            
            # Apply transformations
            transformed_data = {}
            errors = []
            warnings = []
            
            for mapping in field_mappings:
                try:
                    # Extract value from source data
                    value = self._extract_value(data, mapping.source_path)
                    
                    # Apply transformation function if specified
                    if mapping.transform_func:
                        value = self._apply_transform(value, mapping.transform_func)
                    
                    # Convert type if needed
                    if mapping.target_path in target_schema.fields:
                        target_type = target_schema.fields[mapping.target_path].get("type")
                        if target_type:
                            value = self._convert_type(value, DataType(target_type))
                    
                    # Set value in transformed data
                    self._set_nested_value(transformed_data, mapping.target_path, value)
                    
                except Exception as e:
                    error_msg = f"Failed to transform field {mapping.source_path}: {str(e)}"
                    errors.append(error_msg)
                    
                    if mapping.required:
                        if mapping.default_value is not None:
                            self._set_nested_value(transformed_data, mapping.target_path, mapping.default_value)
                            warnings.append(f"Using default value for required field {mapping.target_path}")
                        else:
                            errors.append(f"Missing required field: {mapping.target_path}")
                    elif not self.config.ignore_missing_fields:
                        warnings.append(error_msg)
            
            # Validate transformed data
            if self.config.validate_output:
                validation_errors = self._validate_data(transformed_data, target_schema)
                errors.extend(validation_errors)
            
            result = TransformationResult(
                transformed_data=transformed_data,
                source_data=data,
                target_schema=target_schema,
                errors=errors,
                warnings=warnings,
                metadata={
                    "transformed_at": datetime.utcnow().isoformat(),
                    "source_schema": source_schema.name,
                    "target_schema": target_schema.name,
                    "fields_mapped": len(field_mappings)
                }
            )
            
            self.logger.info(f"Transformation completed with {len(errors)} errors and {len(warnings)} warnings")
            return result
            
        except Exception as e:
            self.logger.error(f"Schema transformation failed: {str(e)}")
            return TransformationResult(
                transformed_data={},
                source_data=data,
                target_schema=target_schema,
                errors=[str(e)],
                metadata={"error": "Transformation failed"}
            )

    def auto_map_fields(self, source_schema: SchemaDefinition, 
                       target_schema: SchemaDefinition) -> List[FieldMapping]:
        """Automatically generate field mappings between schemas.
        
        Args:
            source_schema: Source schema definition
            target_schema: Target schema definition
            
        Returns:
            List[FieldMapping]: Generated field mappings
        """
        mappings = []
        
        for target_field, target_def in target_schema.fields.items():
            # Try exact match first
            if target_field in source_schema.fields:
                mappings.append(FieldMapping(
                    source_path=target_field,
                    target_path=target_field,
                    required=target_field in target_schema.required_fields
                ))
                continue
            
            # Try fuzzy matching
            best_match = self._find_best_field_match(target_field, source_schema.fields.keys())
            if best_match:
                mappings.append(FieldMapping(
                    source_path=best_match,
                    target_path=target_field,
                    required=target_field in target_schema.required_fields
                ))
                continue
            
            # No match found
            if target_field in target_schema.required_fields:
                self.logger.warning(f"No mapping found for required field: {target_field}")
        
        return mappings

    def flatten_nested_data(self, data: Dict[str, Any], 
                           separator: str = ".") -> Dict[str, Any]:
        """Flatten nested dictionary structure.
        
        Args:
            data: Nested data to flatten
            separator: Separator for nested keys
            
        Returns:
            Dict[str, Any]: Flattened data
        """
        def _flatten(obj, parent_key=""):
            items = []
            
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_key = f"{parent_key}{separator}{key}" if parent_key else key
                    if isinstance(value, (dict, list)):
                        items.extend(_flatten(value, new_key).items())
                    else:
                        items.append((new_key, value))
            elif isinstance(obj, list):
                for i, value in enumerate(obj):
                    new_key = f"{parent_key}{separator}{i}" if parent_key else str(i)
                    if isinstance(value, (dict, list)):
                        items.extend(_flatten(value, new_key).items())
                    else:
                        items.append((new_key, value))
            else:
                items.append((parent_key, obj))
            
            return dict(items)
        
        return _flatten(data)

    def unflatten_data(self, data: Dict[str, Any], 
                      separator: str = ".") -> Dict[str, Any]:
        """Unflatten flattened dictionary structure.
        
        Args:
            data: Flattened data
            separator: Separator used in keys
            
        Returns:
            Dict[str, Any]: Nested data
        """
        result = {}
        
        for key, value in data.items():
            keys = key.split(separator)
            current = result
            
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            
            current[keys[-1]] = value
        
        return result

    def _extract_value(self, data: Dict[str, Any], path: str) -> Any:
        """Extract value from nested data structure."""
        keys = path.split(".")
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            elif isinstance(current, list) and key.isdigit():
                index = int(key)
                if 0 <= index < len(current):
                    current = current[index]
                else:
                    raise IndexError(f"Index {index} out of range for list")
            else:
                raise KeyError(f"Key '{key}' not found in path '{path}'")
        
        return current

    def _set_nested_value(self, data: Dict[str, Any], path: str, value: Any) -> None:
        """Set value in nested data structure."""
        keys = path.split(".")
        current = data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value

    def _apply_transform(self, value: Any, transform_func: str) -> Any:
        """Apply transformation function to value."""
        # Built-in transformations
        if transform_func == "upper":
            return str(value).upper()
        elif transform_func == "lower":
            return str(value).lower()
        elif transform_func == "trim":
            return str(value).strip()
        elif transform_func == "abs":
            return abs(float(value))
        elif transform_func == "round":
            return round(float(value))
        else:
            # Could support custom functions here
            self.logger.warning(f"Unknown transform function: {transform_func}")
            return value

    def _convert_type(self, value: Any, target_type: DataType) -> Any:
        """Convert value to target type."""
        if value is None:
            return None
        
        try:
            if target_type == DataType.STRING:
                return str(value)
            elif target_type == DataType.INTEGER:
                return int(float(value))
            elif target_type == DataType.FLOAT:
                return float(value)
            elif target_type == DataType.BOOLEAN:
                if isinstance(value, str):
                    return value.lower() in ("true", "1", "yes", "on")
                return bool(value)
            elif target_type == DataType.ARRAY:
                if isinstance(value, str):
                    return value.split(",")
                elif not isinstance(value, list):
                    return [value]
                return value
            elif target_type == DataType.OBJECT:
                if isinstance(value, str):
                    import json
                    return json.loads(value)
                return value if isinstance(value, dict) else {"value": value}
            else:
                return value
        except Exception as e:
            self.logger.error(f"Type conversion failed: {str(e)}")
            return value

    def _validate_data(self, data: Dict[str, Any], schema: SchemaDefinition) -> List[str]:
        """Validate data against schema."""
        errors = []
        
        # Check required fields
        for field in schema.required_fields:
            if field not in data or data[field] is None:
                errors.append(f"Missing required field: {field}")
        
        # Check field types
        for field, value in data.items():
            if field in schema.fields:
                expected_type = schema.fields[field].get("type")
                if expected_type and not self._check_type(value, DataType(expected_type)):
                    errors.append(f"Invalid type for field {field}: expected {expected_type}")
        
        return errors

    def _check_type(self, value: Any, expected_type: DataType) -> bool:
        """Check if value matches expected type."""
        if expected_type == DataType.STRING:
            return isinstance(value, str)
        elif expected_type == DataType.INTEGER:
            return isinstance(value, int)
        elif expected_type == DataType.FLOAT:
            return isinstance(value, (int, float))
        elif expected_type == DataType.BOOLEAN:
            return isinstance(value, bool)
        elif expected_type == DataType.ARRAY:
            return isinstance(value, list)
        elif expected_type == DataType.OBJECT:
            return isinstance(value, dict)
        return True

    def _find_best_field_match(self, target_field: str, source_fields: List[str]) -> Optional[str]:
        """Find best matching field for target field."""
        # Exact match
        if target_field in source_fields:
            return target_field
        
        # Case-insensitive match
        for field in source_fields:
            if field.lower() == target_field.lower():
                return field
        
        # Substring match
        for field in source_fields:
            if target_field.lower() in field.lower() or field.lower() in target_field.lower():
                return field
        
        return None

    def _initialize_type_converters(self) -> Dict[DataType, Callable]:
        """Initialize type conversion functions."""
        return {
            DataType.STRING: str,
            DataType.INTEGER: lambda x: int(float(x)),
            DataType.FLOAT: float,
            DataType.BOOLEAN: lambda x: str(x).lower() in ("true", "1", "yes") if isinstance(x, str) else bool(x)
        }


# Factory function for easy instantiation
def create_schema_transformer(
    strict_mode: bool = False,
    ignore_missing_fields: bool = True,
    validate_output: bool = True,
    **kwargs
) -> SchemaTransformer:
    """Create a configured schema transformer."""
    config = TransformationConfig(
        strict_mode=strict_mode,
        ignore_missing_fields=ignore_missing_fields,
        validate_output=validate_output,
        **kwargs
    )
    return SchemaTransformer(config)


# Convenience function for direct usage
def transform_output_schema(
    data: Dict[str, Any],
    source_schema: Dict[str, Any],
    target_schema: Dict[str, Any],
    field_mappings: Optional[List[Dict[str, Any]]] = None,
    strict_mode: bool = False
) -> Dict[str, Any]:
    """Transform data between schemas.
    
    Args:
        data: Source data to transform
        source_schema: Source schema definition
        target_schema: Target schema definition
        field_mappings: Optional field mappings
        strict_mode: Whether to enforce strict validation
        
    Returns:
        Dict: Transformation result
    """
    transformer = create_schema_transformer(strict_mode=strict_mode)
    
    # Convert schemas
    source_def = SchemaDefinition(**source_schema)
    target_def = SchemaDefinition(**target_schema)
    
    # Convert mappings
    mappings = []
    if field_mappings:
        for mapping in field_mappings:
            mappings.append(FieldMapping(**mapping))
    else:
        mappings = transformer.auto_map_fields(source_def, target_def)
    
    # Transform
    result = transformer.transform_schema(data, source_def, target_def, mappings)
    
    return {
        "transformed_data": result.transformed_data,
        "errors": result.errors,
        "warnings": result.warnings,
        "metadata": result.metadata
    }
