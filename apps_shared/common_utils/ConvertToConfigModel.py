"""Convert to Config Model - Utility for converting data to configuration models.

This module provides utilities for converting various data formats into
structured configuration models with validation and type safety.
Follows the functional component pattern with proper logging.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class ConfigFormat(Enum):
    """Supported configuration formats."""
    JSON = "json"
    YAML = "yaml"
    DICT = "dict"
    ENV = "env"


class ConversionMode(Enum):
    """Modes for configuration conversion."""
    STRICT = "strict"
    LENIENT = "lenient"
    VALIDATE_ONLY = "validate_only"


@dataclass
class ConfigField:
    """Definition of a configuration field."""
    name: str
    type: str
    required: bool = False
    default_value: object = None
    description: str = ""
    env_var: str | None = None
    validator: str | None = None


@dataclass
class ConfigModel:
    """Configuration model definition."""
    name: str
    version: str
    fields: dict[str, ConfigField]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversionConfig:
    """Configuration for conversion operations."""
    mode: ConversionMode = ConversionMode.LENIENT
    preserve_unknown: bool = True
    convert_types: bool = True
    validate_after: bool = True


@dataclass
class ConversionResult:
    """Result of configuration conversion."""
    config_model: ConfigModel
    converted_data: dict[str, Any]
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class ConfigModelConverter:
    """Main class for converting data to configuration models."""

    def __init__(self, config: ConversionConfig | None = None):
        self.config = config or ConversionConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._type_converters = self._initialize_type_converters()

    def convert_to_model(self, data: str | dict[str, Any],
                        source_format: ConfigFormat,
                        model: ConfigModel) -> ConversionResult:
        """Convert data to configuration model.

        Args:
            data: Input data to convert
            source_format: Format of input data
            model: Target configuration model

        Returns:
            ConversionResult: Conversion result with validated data
        """
        self.logger.info(f"Converting {source_format.value} to config model: {model.name}")

        try:
            # Parse input data based on format
            if source_format == ConfigFormat.JSON:
                parsed_data = self._parse_json(data)
            elif source_format == ConfigFormat.YAML:
                parsed_data = self._parse_yaml(data)
            elif source_format == ConfigFormat.DICT:
                parsed_data = data if isinstance(data, dict) else {}
            elif source_format == ConfigFormat.ENV:
                parsed_data = self._parse_env(data)
            else:
                raise ValueError(f"Unsupported format: {source_format}")

            # Convert and validate against model
            converted_data, errors, warnings = self._convert_to_model(parsed_data, model)

            # Validate after conversion if configured
            if self.config.validate_after and not errors:
                validation_errors = self._validate_model(converted_data, model)
                errors.extend(validation_errors)

            result = ConversionResult(
                config_model=model,
                converted_data=converted_data,
                errors=errors,
                warnings=warnings,
                metadata={
                    "converted_at": datetime.utcnow().isoformat(),
                    "source_format": source_format.value,
                    "conversion_mode": self.config.mode.value
                }
            )

            self.logger.info(f"Conversion completed with {len(errors)} errors and {len(warnings)} warnings")
            return result

        except Exception as e:
            self.logger.error(f"Conversion failed: {str(e)}")
            return ConversionResult(
                config_model=model,
                converted_data={},
                errors=[str(e)],
                metadata={"error": str(e)}
            )

    def convert_from_dict(self, data: dict[str, Any], model: ConfigModel) -> ConversionResult:
        """Convert dictionary to configuration model.

        Args:
            data: Dictionary data to convert
            model: Target configuration model

        Returns:
            ConversionResult: Conversion result
        """
        return self.convert_to_model(data, ConfigFormat.DICT, model)

    def convert_from_json(self, json_str: str, model: ConfigModel) -> ConversionResult:
        """Convert JSON string to configuration model.

        Args:
            json_str: JSON string to convert
            model: Target configuration model

        Returns:
            ConversionResult: Conversion result
        """
        return self.convert_to_model(json_str, ConfigFormat.JSON, model)

    def convert_from_yaml(self, yaml_str: str, model: ConfigModel) -> ConversionResult:
        """Convert YAML string to configuration model.

        Args:
            yaml_str: YAML string to convert
            model: Target configuration model

        Returns:
            ConversionResult: Conversion result
        """
        return self.convert_to_model(yaml_str, ConfigFormat.YAML, model)

    def convert_from_env(self, env_data: str | dict[str, str], model: ConfigModel) -> ConversionResult:
        """Convert environment variables to configuration model.

        Args:
            env_data: Environment variables (string or dict)
            model: Target configuration model

        Returns:
            ConversionResult: Conversion result
        """
        return self.convert_to_model(env_data, ConfigFormat.ENV, model)

    def export_to_dict(self, model: ConfigModel, include_defaults: bool = True) -> dict[str, Any]:
        """Export configuration model to dictionary.

        Args:
            model: Configuration model to export
            include_defaults: Whether to include default values

        Returns:
            Dict: Exported configuration
        """
        result = {}

        for field_name, field_def in model.fields.items():
            if include_defaults or field_def.default_value is not None:
                result[field_name] = field_def.default_value

        return result

    def export_to_json(self, model: ConfigModel, include_defaults: bool = True,
                      indent: int = 2) -> str:
        """Export configuration model to JSON string.

        Args:
            model: Configuration model to export
            include_defaults: Whether to include default values
            indent: JSON indentation

        Returns:
            str: JSON string
        """
        data = self.export_to_dict(model, include_defaults)
        return json.dumps(data, indent=indent, ensure_ascii=False)

    def export_to_yaml(self, model: ConfigModel, include_defaults: bool = True) -> str:
        """Export configuration model to YAML string.

        Args:
            model: Configuration model to export
            include_defaults: Whether to include default values

        Returns:
            str: YAML string
        """
        data = self.export_to_dict(model, include_defaults)
        return yaml.dump(data, default_flow_style=False, allow_unicode=True)

    def _parse_json(self, data: str | dict[str, Any]) -> dict[str, Any]:
        """Parse JSON data."""
        if isinstance(data, str):
            return json.loads(data)
        elif isinstance(data, dict):
            return data
        else:
            raise ValueError("Invalid JSON data type")

    def _parse_yaml(self, data: str | dict[str, Any]) -> dict[str, Any]:
        """Parse YAML data."""
        if isinstance(data, str):
            return yaml.safe_load(data) or {}
        elif isinstance(data, dict):
            return data
        else:
            raise ValueError("Invalid YAML data type")

    def _parse_env(self, data: str | dict[str, str]) -> dict[str, Any]:
        """Parse environment variables."""
        if isinstance(data, str):
            # Parse .env format string
            env_dict = {}
            for line in data.strip().split('\n'):
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_dict[key.strip()] = value.strip().strip('"\'')
            return env_dict
        elif isinstance(data, dict):
            return data
        else:
            raise ValueError("Invalid environment data type")

    def _get_field_value(self, field_name: str, field_def: Any, data: dict[str, Any]) -> Any:
        """Get field value from data or environment."""
        if field_name in data:
            return data[field_name]
        if field_def.env_var and field_def.env_var in data:
            return data[field_def.env_var]
        return None

    def _handle_missing_value(self, field_name: str, field_def: ConfigField, errors: list[str], warnings: list[str]) -> Any:
        """Handle missing field value."""
        if field_def.required:
            if self.config.mode == ConversionMode.STRICT:
                errors.append(f"Required field missing: {field_name}")
                return None
            elif field_def.default_value is not None:
                warnings.append(f"Using default value for {field_name}")
                return field_def.default_value
            else:
                warnings.append(f"Optional field missing: {field_name}")
                return None
        elif field_def.default_value is not None:
            return field_def.default_value
        return None

    def _convert_field_type(self, value: Any, field_name: str, field_def: ConfigField, errors: list[str], warnings: list[str]) -> Any:
        """Convert field type with error handling."""
        if not self.config.convert_types:
            return value

        try:
            return self._convert_type(value, field_def.type)
        except Exception as e:
            if self.config.mode == ConversionMode.STRICT:
                errors.append(f"Type conversion failed for {field_name}: {str(e)}")
            else:
                warnings.append(f"Type conversion failed for {field_name}: {str(e)}")
            return field_def.default_value

    def _validate_field_value(self, value: Any, field_name: str, field_def: ConfigField, errors: list[str], warnings: list[str]) -> None:
        """Validate field value."""
        if value is None or not field_def.validator:
            return

        if not self._validate_field(value, field_def.validator):
            if self.config.mode == ConversionMode.STRICT:
                errors.append(f"Validation failed for field: {field_name}")
            else:
                warnings.append(f"Validation failed for field: {field_name}")

    def _convert_to_model(self, data: dict[str, Any],
                         model: ConfigModel) -> tuple[dict[str, Any], list[str], list[str]]:
        """Convert data to match configuration model."""
        converted = {}
        errors = []
        warnings = []

        for field_name, field_def in model.fields.items():
            value = self._get_field_value(field_name, field_def, data)

            if value is None:
                value = self._handle_missing_value(field_name, field_def, errors, warnings)
            else:
                value = self._convert_field_type(value, field_name, field_def, errors, warnings)

            self._validate_field_value(value, field_name, field_def, errors, warnings)

            if value is not None:
                converted[field_name] = value

        # Handle unknown fields
        if self.config.preserve_unknown:
            for key, value in data.items():
                if key not in model.fields and key not in converted:
                    converted[key] = value
                    warnings.append(f"Preserved unknown field: {key}")
        elif self.config.mode == ConversionMode.STRICT:
            for key in data:
                if key not in model.fields:
                    errors.append(f"Unknown field: {key}")

        return converted, errors, warnings

    def _convert_type(self, value: object, target_type: str) -> object:
        """Convert value to target type."""
        if target_type in self._type_converters:
            return self._type_converters[target_type](value)
        else:
            return value

    def _validate_field(self, value: object, validator: str) -> bool:
        """Validate field value using validator."""
        # Built-in validators
        if validator == "positive":
            return isinstance(value, (int, float)) and value > 0
        elif validator == "non_negative":
            return isinstance(value, (int, float)) and value >= 0
        elif validator == "non_empty":
            return isinstance(value, str) and len(value.strip()) > 0
        elif validator == "email":
            return isinstance(value, str) and "@" in value
        elif validator == "url":
            return isinstance(value, str) and (value.startswith("http://") or value.startswith("https://"))
        else:
            # Could support custom validators here
            return True

    def _validate_model(self, data: dict[str, Any], model: ConfigModel) -> list[str]:
        """Validate converted data against model."""
        errors = []

        # Check all required fields are present
        for field_name, field_def in model.fields.items():
            if field_def.required and field_name not in data:
                errors.append(f"Required field missing after conversion: {field_name}")

        return errors

    def _initialize_type_converters(self) -> dict[str, Callable]:
        """Initialize type conversion functions."""
        return {
            "string": str,
            "int": int,
            "float": float,
            "bool": lambda x: str(x).lower() in ("true", "1", "yes", "on") if isinstance(x, str) else bool(x),
            "list": lambda x: list(x) if not isinstance(x, list) else x,
            "dict": lambda x: dict(x) if not isinstance(x, dict) else x
        }


# Factory function for easy instantiation
def create_config_model_converter(
    mode: str = "lenient",
    preserve_unknown: bool = True,
    convert_types: bool = True,
    **kwargs: object
) -> ConfigModelConverter:
    """Create a configured config model converter."""
    config = ConversionConfig(
        mode=ConversionMode(mode),
        preserve_unknown=preserve_unknown,
        convert_types=convert_types,
        **kwargs
    )
    return ConfigModelConverter(config)


# Convenience function for direct usage
def convert_to_config_model(
    data: str | dict[str, Any],
    model_definition: dict[str, Any],
    source_format: str = "dict",
    mode: str = "lenient"
) -> dict[str, Any]:
    """Convert data to configuration model.

    Args:
        data: Input data to convert
        model_definition: Configuration model definition
        source_format: Format of input data
        mode: Conversion mode

    Returns:
        Dict: Conversion result
    """
    converter = create_config_model_converter(mode=mode)

    # Convert model definition
    fields = {}
    for name, field_def in model_definition.get("fields", {}).items():
        fields[name] = ConfigField(
            name=name,
            type=field_def.get("type", "string"),
            required=field_def.get("required", False),
            default_value=field_def.get("default"),
            description=field_def.get("description", ""),
            env_var=field_def.get("env_var"),
            validator=field_def.get("validator")
        )

    model = ConfigModel(
        name=model_definition.get("name", "unnamed"),
        version=model_definition.get("version", "1.0"),
        fields=fields,
        metadata=model_definition.get("metadata", {})
    )

    # Convert
    result = converter.convert_to_model(data, ConfigFormat(source_format), model)

    return {
        "config_model": {
            "name": result.config_model.name,
            "version": result.config_model.version,
            "metadata": result.config_model.metadata
        },
        "converted_data": result.converted_data,
        "errors": result.errors,
        "warnings": result.warnings,
        "metadata": result.metadata
    }
