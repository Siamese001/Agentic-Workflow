#!/usr/bin/env python3
"""Validate YAML configuration files against JSON schemas.

This script is run in CI to ensure all YAML config files are valid.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

# Optional jsonschema import - fallback to basic validation if not available
try:
    from jsonschema import ValidationError, validate
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

CONFIG_DIR = Path("config")
SCHEMA_DIR = CONFIG_DIR / "schemas"

# Map of YAML files to their schemas
SCHEMA_MAP = {
    "token_budget.yaml": "token_budget.schema.json",
    "structure_blueprint/territories.yaml": "structure_blueprint.schema.json",
    "structure_blueprint/layers.yaml": "layer_overrides.schema.json",
}


def load_yaml(path: Path) -> Any:
    """Load YAML file."""
    with open(path) as f:
        return yaml.safe_load(f)


def load_schema(path: Path) -> dict:
    """Load JSON schema."""
    with open(path) as f:
        return json.load(f)


def validate_basic(yaml_data: Any, schema: dict, path: str) -> list[str]:
    """Basic validation without jsonschema library."""
    errors = []

    # Check required fields at root
    required = schema.get("required", [])
    for field in required:
        if field not in yaml_data:
            errors.append(f"Missing required field: {field}")

    # Check type of root
    schema_type = schema.get("type")
    if schema_type == "object" and not isinstance(yaml_data, dict):
        errors.append(f"Expected object, got {type(yaml_data).__name__}")

    # Check properties
    properties = schema.get("properties", {})
    for prop, prop_schema in properties.items():
        if prop in yaml_data:
            value = yaml_data[prop]
            prop_type = prop_schema.get("type")

            if prop_type == "string" and not isinstance(value, str):
                errors.append(f"{path}.{prop}: expected string, got {type(value).__name__}")
            elif prop_type == "integer" and not isinstance(value, int):
                errors.append(f"{path}.{prop}: expected integer, got {type(value).__name__}")
            elif prop_type == "object" and not isinstance(value, dict):
                errors.append(f"{path}.{prop}: expected object, got {type(value).__name__}")
            elif prop_type == "array" and not isinstance(value, list):
                errors.append(f"{path}.{prop}: expected array, got {type(value).__name__}")

    return errors


def validate_file(yaml_path: Path, schema_path: Path) -> tuple[bool, list[str]]:
    """Validate a YAML file against its schema."""
    errors = []

    try:
        yaml_data = load_yaml(yaml_path)
    except yaml.YAMLError as e:
        return False, [f"YAML parse error: {e}"]
    except Exception as e:
        return False, [f"Error loading YAML: {e}"]

    try:
        schema = load_schema(schema_path)
    except Exception as e:
        return False, [f"Error loading schema: {e}"]

    if HAS_JSONSCHEMA:
        try:
            validate(yaml_data, schema)
            return True, []
        except ValidationError as e:
            return False, [f"Validation error: {e.message} at {list(e.path)}"]
    else:
        # Fallback to basic validation
        errors = validate_basic(yaml_data, schema, yaml_path.name)
        return len(errors) == 0, errors


def main() -> int:
    """Validate all YAML configs."""
    all_valid = True

    print("=== YAML Configuration Validation ===\n")

    for yaml_file, schema_file in SCHEMA_MAP.items():
        yaml_path = CONFIG_DIR / yaml_file
        schema_path = SCHEMA_DIR / schema_file

        print(f"Validating {yaml_file}...")

        if not yaml_path.exists():
            print(f"  ✗ NOT FOUND: {yaml_path}")
            all_valid = False
            continue

        if not schema_path.exists():
            print(f"  ✗ SCHEMA NOT FOUND: {schema_path}")
            all_valid = False
            continue

        valid, errors = validate_file(yaml_path, schema_path)

        if valid:
            print("  ✓ VALID")
        else:
            print("  ✗ INVALID")
            for error in errors:
                print(f"    - {error}")
            all_valid = False

    print()
    if all_valid:
        print("=== All YAML configurations valid ===")
        return 0
    else:
        print("=== Some YAML configurations invalid ===")
        return 1


if __name__ == "__main__":
    sys.exit(main())
