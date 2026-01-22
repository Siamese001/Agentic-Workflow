"""Convert to Internal Schema - Utility for converting data to internal schema format.

This module provides utilities for converting external data formats into the
internal schema format used by the system, with proper validation and mapping.
Follows the functional component pattern with proper logging.
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class SchemaType(Enum):
    """Types of schemas supported."""

    JSON_SCHEMA = "json_schema"
    AVRO = "avro"
    PROTOBUF = "protobuf"
    CUSTOM = "custom"


class ConversionStrategy(Enum):
    """Strategies for schema conversion."""

    STRICT = "strict"
    LENIENT = "lenient"
    MAP_ONLY = "map_only"
    VALIDATE_ONLY = "validate_only"


@dataclass
class FieldMapping:
    """Mapping between external and internal fields."""

    external_path: str
    internal_path: str
    type_conversion: str | None = None
    required: bool = False
    default_value: Any = None
    transform_func: str | None = None


@dataclass
class InternalSchema:
    """Definition of internal schema format."""

    name: str
    version: str
    namespace: str
    fields: dict[str, dict[str, Any]]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversionConfig:
    """Configuration for schema conversion."""

    strategy: ConversionStrategy = ConversionStrategy.LENIENT
    preserve_unknown: bool = False
    validate_types: bool = True
    apply_transforms: bool = True


@dataclass
class ConversionResult:
    """Result of schema conversion."""

    internal_schema: InternalSchema
    converted_data: dict[str, Any]
    field_mappings: list[FieldMapping]
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class InternalSchemaConverter:
    """Main class for converting data to internal schema format."""

    def __init__(self, config: ConversionConfig | None = None):
        self.config = config or ConversionConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._type_converters = self._initialize_type_converters()
        self._transform_functions = self._initialize_transform_functions()

    def _validate_external_schema(
        self,
        external_data: dict[str, Any],
        external_schema: dict[str, Any] | None,
        errors: list[str],
        warnings: list[str],
    ) -> None:
        """Validate external data against schema."""
        if not external_schema or not self.config.validate_types:
            return

        validation_errors = self._validate_external_data(external_data, external_schema)
        if validation_errors and self.config.strategy == ConversionStrategy.STRICT:
            errors.extend(validation_errors)
        else:
            warnings.extend(validation_errors)

    def _process_field_mapping(
        self,
        mapping: FieldMapping,
        external_data: dict[str, Any],
        converted_data: dict[str, Any],
        errors: list[str],
        warnings: list[str],
    ) -> None:
        """Process a single field mapping."""
        try:
            external_value = self._extract_and_transform_value(
                mapping, external_data, errors, warnings
            )
            self._set_converted_value(mapping, external_value, converted_data, errors, warnings)
        except Exception as e:
            error_msg = f"Failed to map field {mapping.external_path}: {str(e)}"
            if mapping.required:
                errors.append(error_msg)
            else:
                warnings.append(error_msg)

    def _extract_and_transform_value(
        self,
        mapping: FieldMapping,
        external_data: dict[str, object],
        errors: list[str],
        warnings: list[str],
    ) -> object:
        """Extract and transform value from external data."""
        external_value = self._extract_nested_value(external_data, mapping.external_path)

        if mapping.transform_func and self.config.apply_transforms:
            external_value = self._apply_transform(external_value, mapping.transform_func)

        if mapping.type_conversion:
            external_value = self._convert_with_error_handling(
                external_value, mapping, errors, warnings
            )

        return external_value

    def _convert_with_error_handling(
        self, value: Any, mapping: FieldMapping, errors: list[str], warnings: list[str]
    ) -> object:
        """Convert type with error handling."""
        try:
            return self._convert_type(value, mapping.type_conversion)
        except Exception as e:
            error_msg = f"Type conversion failed for {mapping.external_path}: {str(e)}"
            if self.config.strategy == ConversionStrategy.STRICT:
                errors.append(error_msg)
            else:
                warnings.append(error_msg)
            return mapping.default_value

    def _set_converted_value(
        self,
        mapping: FieldMapping,
        external_value: object,
        converted_data: dict[str, object],
        errors: list[str],
        warnings: list[str],
    ) -> None:
        """Set converted value in internal data."""
        if external_value is not None:
            self._set_nested_value(converted_data, mapping.internal_path, external_value)
        elif mapping.required:
            self._handle_missing_required_field(mapping, converted_data, errors, warnings)

    def _handle_missing_required_field(
        self,
        mapping: FieldMapping,
        converted_data: dict[str, object],
        errors: list[str],
        warnings: list[str],
    ) -> None:
        """Handle missing required field."""
        if mapping.default_value is not None:
            self._set_nested_value(converted_data, mapping.internal_path, mapping.default_value)
            warnings.append(f"Using default for required field: {mapping.internal_path}")
        else:
            errors.append(f"Missing required field: {mapping.internal_path}")

    def _finalize_conversion(
        self, converted_data: dict[str, object], internal_schema: InternalSchema, errors: list[str]
    ) -> None:
        """Finalize conversion with validation and cleanup."""
        if not self.config.preserve_unknown:
            self._remove_unknown_fields(converted_data, internal_schema)

        if self.config.validate_types:
            validation_errors = self._validate_internal_data(converted_data, internal_schema)
            errors.extend(validation_errors)

    def convert_to_internal(
        self,
        external_data: dict[str, object],
        internal_schema: InternalSchema,
        field_mappings: list[FieldMapping],
        external_schema: dict[str, object] | None = None,
    ) -> ConversionResult:
        """Convert external data to internal schema format."""
        self.logger.info(f"Converting to internal schema: {internal_schema.name}")

        try:
            converted_data = {}
            errors = []
            warnings = []

            self._validate_external_schema(external_data, external_schema, errors, warnings)

            for mapping in field_mappings:
                self._process_field_mapping(
                    mapping, external_data, converted_data, errors, warnings
                )

            self._finalize_conversion(converted_data, internal_schema, errors)

            result = ConversionResult(
                internal_schema=internal_schema,
                converted_data=converted_data,
                field_mappings=field_mappings,
                errors=errors,
                warnings=warnings,
                metadata={
                    "converted_at": datetime.utcnow().isoformat(),
                    "conversion_strategy": self.config.strategy.value,
                    "external_fields": len(external_data),
                    "internal_fields": len(converted_data),
                },
            )

            self.logger.info(
                f"Conversion completed with {len(errors)} errors and {len(warnings)} warnings"
            )
            return result

        except Exception as e:
            self.logger.error(f"Schema conversion failed: {str(e)}")
            return ConversionResult(
                internal_schema=internal_schema,
                converted_data={},
                field_mappings=field_mappings,
                errors=[str(e)],
                metadata={"error": str(e)},
            )

    def auto_generate_mappings(
        self, external_schema: dict[str, object], internal_schema: InternalSchema
    ) -> list[FieldMapping]:
        """Automatically generate field mappings between schemas.

        Args:
            external_schema: External schema definition
            internal_schema: Internal schema definition

        Returns:
            List[FieldMapping]: Generated field mappings
        """
        mappings = []
        external_fields = self._extract_schema_fields(external_schema)

        for internal_field, internal_def in internal_schema.fields.items():
            # Try exact match first
            if internal_field in external_fields:
                mappings.append(
                    FieldMapping(
                        external_path=internal_field,
                        internal_path=internal_field,
                        type_conversion=internal_def.get("type"),
                        required=internal_def.get("required", False),
                    )
                )
                continue

            # Try fuzzy matching
            best_match = self._find_best_field_match(internal_field, external_fields.keys())
            if best_match:
                mappings.append(
                    FieldMapping(
                        external_path=best_match,
                        internal_path=internal_field,
                        type_conversion=internal_def.get("type"),
                        required=internal_def.get("required", False),
                    )
                )
                continue

            # No match found
            if internal_def.get("required", False):
                self.logger.warning(f"No mapping found for required field: {internal_field}")

        return mappings

    def convert_batch(
        self,
        external_data_list: list[dict[str, object]],
        external_schema: dict[str, object] | None = None,
        internal_schema: InternalSchema = None,
        field_mappings: list[FieldMapping] = None,
    ) -> list[ConversionResult]:
        """Convert multiple external data items.

        Args:
            external_data_list: List of external data items
            external_schema: Optional external schema
            internal_schema: Internal schema
            field_mappings: Field mappings to use

        Returns:
            List[ConversionResult]: Results for each item
        """
        results = []

        for i, external_data in enumerate(external_data_list):
            self.logger.debug(f"Converting item {i + 1}/{len(external_data_list)}")
            result = self.convert_to_internal(
                external_data, external_schema, internal_schema, field_mappings
            )
            results.append(result)

        return results

    def _extract_nested_value(self, data: dict[str, object], path: str) -> object:
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
                    raise IndexError(f"Index {index} out of range")
            else:
                raise KeyError(f"Key '{key}' not found in path '{path}'")

        return current

    def _set_nested_value(self, data: dict[str, object], path: str, value: object) -> None:
        """Set value in nested data structure."""
        keys = path.split(".")
        current = data

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value

    def _apply_transform(self, value: object, transform_func: str) -> object:
        """Apply transformation function to value."""
        if transform_func in self._transform_functions:
            return self._transform_functions[transform_func](value)
        else:
            self.logger.warning(f"Unknown transform function: {transform_func}")
            return value

    def _convert_type(self, value: object, target_type: str) -> object:
        """Convert value to target type."""
        if target_type in self._type_converters:
            return self._type_converters[target_type](value)
        else:
            return value

    def _validate_external_data(self, data: dict[str, Any], schema: dict[str, Any]) -> list[str]:
        """Validate external data against external schema."""
        errors = []

        # Simple validation - can be enhanced
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field in external data: {field}")

        return errors

    def _validate_internal_data(self, data: dict[str, Any], schema: InternalSchema) -> list[str]:
        """Validate internal data against internal schema."""
        errors = []

        for field_name, field_def in schema.fields.items():
            if field_def.get("required", False) and field_name not in data:
                errors.append(f"Missing required field in internal data: {field_name}")

        return errors

    def _extract_schema_fields(self, schema: dict[str, Any]) -> dict[str, dict[str, Any]]:
        """Extract field definitions from schema."""
        fields = {}

        if "properties" in schema:
            fields.update(schema["properties"])
        elif "fields" in schema:
            fields.update(schema["fields"])
        elif isinstance(schema, dict):
            # Assume schema itself is the fields definition
            for key, value in schema.items():
                if isinstance(value, dict) and "type" in value:
                    fields[key] = value

        return fields

    def _find_best_field_match(self, target_field: str, candidate_fields: list[str]) -> str | None:
        """Find best matching field for target field."""
        # Exact match
        if target_field in candidate_fields:
            return target_field

        # Case-insensitive match
        for field in candidate_fields:
            if field.lower() == target_field.lower():
                return field

        # Substring match
        for field in candidate_fields:
            if target_field.lower() in field.lower() or field.lower() in target_field.lower():
                return field

        return None

    def _remove_unknown_fields(self, data: dict[str, Any], schema: InternalSchema) -> None:
        """Remove fields not defined in schema."""

        def _remove_unknown_recursive(obj, path=""):
            if isinstance(obj, dict):
                keys_to_remove = []
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key

                    if current_path not in schema.fields:
                        keys_to_remove.append(key)
                    else:
                        _remove_unknown_recursive(value, current_path)

                for key in keys_to_remove:
                    del obj[key]

        _remove_unknown_recursive(data)

    def _initialize_type_converters(self) -> dict[str, Callable]:
        """Initialize type conversion functions."""
        return {
            "string": str,
            "integer": int,
            "float": float,
            "boolean": lambda x: str(x).lower() in ("true", "1", "yes")
            if isinstance(x, str)
            else bool(x),
            "array": list,
            "object": dict,
        }

    def _initialize_transform_functions(self) -> dict[str, Callable]:
        """Initialize transformation functions."""
        return {
            "upper": lambda x: str(x).upper(),
            "lower": lambda x: str(x).lower(),
            "trim": lambda x: str(x).strip(),
            "abs": abs,
            "round": round,
            "timestamp_to_iso": lambda x: datetime.fromtimestamp(x).isoformat()
            if isinstance(x, (int, float))
            else x,
            "iso_to_timestamp": lambda x: datetime.fromisoformat(x).timestamp()
            if isinstance(x, str)
            else x,
        }


# Factory function for easy instantiation
def create_internal_schema_converter(
    strategy: str = "lenient",
    preserve_unknown: bool = False,
    validate_types: bool = True,
    **kwargs: dict[str, object],
) -> InternalSchemaConverter:
    """Create a configured internal schema converter."""
    config = ConversionConfig(
        strategy=ConversionStrategy(strategy),
        preserve_unknown=preserve_unknown,
        validate_types=validate_types,
        **kwargs,
    )
    return InternalSchemaConverter(config)


# Convenience function for direct usage
def convert_to_internal_schema(
    external_data: dict[str, Any],
    internal_schema_def: dict[str, Any],
    field_mappings: list[dict[str, Any]] | None = None,
    external_schema: dict[str, Any] | None = None,
    strategy: str = "lenient",
) -> dict[str, Any]:
    """Convert data to internal schema format.

    Args:
        external_data: External data to convert
        internal_schema_def: Internal schema definition
        field_mappings: Optional field mappings
        external_schema: Optional external schema
        strategy: Conversion strategy

    Returns:
        Dict: Conversion result
    """
    converter = create_internal_schema_converter(strategy=strategy)

    # Convert internal schema
    internal_schema = InternalSchema(
        name=internal_schema_def.get("name", "unnamed"),
        version=internal_schema_def.get("version", "1.0"),
        namespace=internal_schema_def.get("namespace", "default"),
        fields=internal_schema_def.get("fields", {}),
        metadata=internal_schema_def.get("metadata", {}),
    )

    # Convert mappings
    mappings = []
    if field_mappings:
        for mapping in field_mappings:
            mappings.append(FieldMapping(**mapping))
    else:
        # Auto-generate if external schema provided
        if external_schema:
            mappings = converter.auto_generate_mappings(external_schema, internal_schema)

    # Convert
    result = converter.convert_to_internal(
        external_data, external_schema, internal_schema, mappings
    )

    return {
        "internal_schema": {
            "name": result.internal_schema.name,
            "version": result.internal_schema.version,
            "namespace": result.internal_schema.namespace,
        },
        "converted_data": result.converted_data,
        "field_mappings": [
            {
                "external_path": m.external_path,
                "internal_path": m.internal_path,
                "type_conversion": m.type_conversion,
                "required": m.required,
            }
            for m in result.field_mappings
        ],
        "errors": result.errors,
        "warnings": result.warnings,
        "metadata": result.metadata,
    }