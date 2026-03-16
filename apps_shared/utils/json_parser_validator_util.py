"""
JSON Parser Utilities - Phase 4 Optimization
Native Python implementations for JSON parsing and manipulation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "json_parser_validator_util", "p0_governance")
_emit_reads_policy_state("p0", "json_parser_validator_util", "policy_binding")
_emit_snapshots_state("p0", "json_parser_validator_util", "state_snapshot")
emit_replay_key("p0", "json_parser_validator_util")
emit_determinism_digest("p0", "json_parser_validator_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


@dataclass
class ParseResult:
    """Result of a JSON parsing operation."""

    success: bool
    data: Any
    errors: list[str]
    metadata: dict[str, Any]


class JsonParser:
    """Native Python JSON parsing utilities."""

    @staticmethod
    def parse_json(json_string: str, strict: bool = True) -> ParseResult:
        """
        Parse JSON string.

        Args:
            json_string: JSON string to parse
            strict: Whether to use strict parsing

        Returns:
            ParseResult with parsed data or errors
        """
        try:
            data = json.loads(json_string, strict=strict)
            return ParseResult(success=True, data=data, errors=[], metadata={})
        except json.JSONDecodeError as e:
            return ParseResult(
                success=False,
                data=None,
                errors=[f"JSON decode error: {str(e)}"],
                metadata={"line": e.lineno, "column": e.colno},
            )
        except Exception as e:
            return ParseResult(success=False, data=None, errors=[f"Parse error: {str(e)}"], metadata={})

    @staticmethod
    def safe_get(data: dict[str, Any], path: str, default: Any = None) -> Any:
        """
        Safely get nested value from dictionary using dot notation.

        Args:
            data: Dictionary to search
            path: Dot-separated path (e.g., "user.profile.name")
            default: Default value if path not found

        Returns:
            Value at path or default
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "JsonParser.safe_get")

        keys = path.split(".")
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current

    @staticmethod
    def safe_set(data: dict[str, Any], path: str, value: Any) -> None:
        """
        Safely set nested value in dictionary using dot notation.

        Args:
            data: Dictionary to modify
            path: Dot-separated path
            value: Value to set
        """
        keys = path.split(".")
        current = data
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value

    @staticmethod
    def merge_dicts(dict1: dict[str, Any], dict2: dict[str, Any], deep: bool = True) -> dict[str, Any]:
        """
        Merge two dictionaries.

        Args:
            dict1: First dictionary
            dict2: Second dictionary (takes precedence)
            deep: Whether to perform deep merge

        Returns:
            Merged dictionary
        """
        result = dict1.copy()
        for key, value in dict2.items():
            if deep and key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = JsonParser.merge_dicts(result[key], value, deep=True)
            else:
                result[key] = value
        return result

    @staticmethod
    def flatten_dict(data: dict[str, Any], separator: str = ".") -> dict[str, Any]:
        """
        Flatten nested dictionary.

        Args:
            data: Dictionary to flatten
            separator: Separator for nested keys

        Returns:
            Flattened dictionary
        """
        result = {}

        def _flatten(obj: Any, prefix: str = "") -> None:
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_key = f"{prefix}{separator}{key}" if prefix else key
                    _flatten(value, new_key)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_key = f"{prefix}{separator}{i}" if prefix else str(i)
                    _flatten(item, new_key)
            else:
                result[prefix] = obj

        _flatten(data)
        return result

    @staticmethod
    def unflatten_dict(data: dict[str, Any], separator: str = ".") -> dict[str, Any]:
        """
        Unflatten dictionary with dot-separated keys.

        Args:
            data: Flattened dictionary
            separator: Separator used in keys

        Returns:
            Unflattened dictionary
        """
        result = {}
        for key, value in data.items():
            JsonParser.safe_set(result, key.replace(separator, "."), value)
        return result

    @staticmethod
    def filter_keys(data: dict[str, Any], keys: list[str], include: bool = True) -> dict[str, Any]:
        """
        Filter dictionary by keys.

        Args:
            data: Dictionary to filter
            keys: List of keys to include/exclude
            include: If True, include only these keys; if False, exclude them

        Returns:
            Filtered dictionary
        """
        if include:
            return {k: v for k, v in data.items() if k in keys}
        else:
            return {k: v for k, v in data.items() if k not in keys}

    @staticmethod
    def validate_schema(data: dict[str, Any], schema: dict[str, type]) -> ParseResult:
        """
        Validate data against simple schema.

        Args:
            data: Data to validate
            schema: Dictionary mapping keys to expected types

        Returns:
            ParseResult with validation results
        """
        errors = []
        for key, expected_type in schema.items():
            if key not in data:
                errors.append(f"Missing required key: {key}")
            elif not isinstance(data[key], expected_type):
                actual_type = type(data[key]).__name__
                expected_name = expected_type.__name__
                errors.append(f"Key '{key}' has wrong type: expected {expected_name}, got {actual_type}")
        if errors:
            return ParseResult(success=False, data=data, errors=errors, metadata={})
        else:
            return ParseResult(success=True, data=data, errors=[], metadata={})

    @staticmethod
    def extract_values(data: dict | list, key: str) -> list[Any]:
        """
        Extract all values for a key from nested structure.

        Args:
            data: Dictionary or list to search
            key: Key to extract

        Returns:
            List of all values found for key
        """
        results = []

        def _extract(obj: Any) -> None:
            if isinstance(obj, dict):
                if key in obj:
                    results.append(obj[key])
                for value in obj.values():
                    _extract(value)
            elif isinstance(obj, list):
                for item in obj:
                    _extract(item)

        _extract(data)
        return results

    @staticmethod
    def transform_keys(data: dict[str, Any], transformer: callable) -> dict[str, Any]:
        """
        Transform all keys in dictionary.

        Args:
            data: Dictionary to transform
            transformer: Function to transform keys

        Returns:
            Dictionary with transformed keys
        """
        result = {}
        for key, value in data.items():
            new_key = transformer(key)
            if isinstance(value, dict):
                result[new_key] = JsonParser.transform_keys(value, transformer)
            else:
                result[new_key] = value
        return result

    @staticmethod
    def to_camel_case(snake_str: str) -> str:
        """Convert snake_case to camelCase."""
        components = snake_str.split("_")
        return components[0] + "".join(x.title() for x in components[1:])

    @staticmethod
    def to_snake_case(camel_str: str) -> str:
        """Convert camelCase to snake_case."""
        import re

        s1 = re.sub("(.)([A-Z][a-z]+)", "\\1_\\2", camel_str)
        return re.sub("([a-z0-9])([A-Z])", "\\1_\\2", s1).lower()
